import calendar
from decimal import Decimal
from dateutil import relativedelta
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.db.models import F, Q, Sum
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from newsroom.models import Author

from . import forms, models


'''There is business logic in this view that belongs in themodel.
TO DO: Refactor by moving filtering by year and month, and calculations
into model.
'''


@login_required
def invoice_list_new(request,
                     year_begin=None, month_begin=None,
                     year_end=None, month_end=None,
                     author=None):

    now = timezone.now()
    # Set staff status
    user = request.user
    if user.is_staff and user.has_perm("payment.change_invoice"):
        staff_view = True
    else:
        staff_view = False

    # Block anyone who isn't supposed to be here
    try:
        if not user.is_authenticated:
            raise Http404
        if staff_view is False:
            if not user.author or user.author.freelancer == False:
                raise Http404
            if author is not None and int(author) != 0:
                if author != user.author.pk:
                    raise Http404
    except: # Let's not risk any unwarranted access
        raise Http404

    # Set date fields to coherent values
    try:
        if year_begin is None:
            year_begin = now.year
        else:
            year_begin = int(year_begin)
        if month_begin is None:
            month_begin = now.month
        else:
            month_begin = int(month_begin)
            if month_begin < 1:
                raise Http404
        if year_end is None:
            year_end = now.year
        else:
            year_end = int(year_end)
        if month_end is None:
            month_end = now.month
        else:
            month_end = int(month_end)
            if month_end > 12:
                raise Http404
        year_month_begin = timezone.datetime(year_begin, month_begin, 1)
        year_month_end = timezone.datetime(year_end, month_end, 1)
        last_day = calendar.monthrange(year_month_end.year,
                                       year_month_end.month)[1]
        year_month_end = timezone.datetime(year_end, month_end, last_day)
    except:
        raise Http404


    # Extract only between start and end dates (inclusive)
    query = Q(date_time_processed__gte=year_month_begin) & \
            Q(date_time_processed__lte=year_month_end)

    # # If it's not the latest period, filter out unpaid items
    # old_period = False
    # if year_month_end.year < now.year:
    #     old_period = True
    # if year_month_end.year == now.year and year_month_end.month < now.month:
    #     old_period = True

    # Filter author
    if staff_view:
        if author is not None and author != 0:
            author = get_object_or_404(Author, pk=author)
            query = query &  Q(author=author)
    else:     # Filter out unauthorised records
        author = get_object_or_404(Author, pk=user.author.pk)
        query = query &  Q(author=author)
        query = query & (Q(status__lte="4") & Q(status__gte="0"))

    if author is None or author == 0:
        author_pk = 0
    else:
        author_pk = author.pk

    invoices = models.Invoice.objects.filter(query)

    # Calculated values
    total_paid = invoices.filter(status="4").aggregate(
        amount_paid=Sum(F('amount_paid') + F('vat_paid') +
                    F('tax_paid')))["amount_paid"]
    total_outstanding = invoices.filter(status__lt="4").\
            aggregate(amount_paid=Sum(F('amount_paid') + F('vat_paid') +
                                    F('tax_paid')))["amount_paid"]
    if total_paid is None:
        total_paid = Decimal(0.0)
    if total_outstanding is None:
        total_outstanding = Decimal(0.0)

    total = total_paid + total_outstanding

    previous_month = year_month_begin - relativedelta.relativedelta(months=1)
    next_month = year_month_end + relativedelta.relativedelta(months=1)

    return render(request, "payment/invoice_list.html",
                  {'invoices': invoices,
                   'total_paid': total_paid,
                   'total_outstanding': total_outstanding,
                   'total': total,
                   'from_date': year_month_begin,
                   'end_date' : year_month_end,
                   'next_month': next_month,
                   'previous_month': previous_month,
                   'latest_month': now,
                   'author': author,
                   'author_pk': author_pk,
                   'staff_view': staff_view})

@login_required
def invoice_detail(request, author_pk, invoice_num, print_view=False):
    user = request.user
    can_edit = False

    if not user.is_authenticated:
        raise Http404
    staff_view = False

    if user.is_staff and user.has_perm("payment.change_invoice"):
        staff_view = True
        can_edit = True
    else:
        if request.user.author is None:
            raise Http404
        if request.user.author.pk != int(author_pk):
            raise Http404
        staff_view = False

    CommissionFormSet = modelformset_factory(models.Commission,
                                             fields=('commission_due',
                                                     'taxable',
                                                     'vatable',
                                                     'fund',
                                                     'deleted',),
                                             extra=0)
    invoice = get_object_or_404(models.Invoice, author__pk=author_pk,
                                invoice_num=invoice_num)
    if request.method == 'POST':
        if staff_view:
            form = forms.InvoiceStaffForm(request.POST, instance=invoice)
        else:
            form = forms.InvoiceForm(request.POST, instance=invoice)

        if form.is_valid():
            invoice = form.save(commit=False)
            if "begin_button" in request.POST and invoice.status != "-":
                invoice.status = "-"
                messages.add_message(request, messages.INFO,
                                     "Status changed to UNPROCESSED")
                invoice.save()
            if "return_button" in request.POST and invoice.status != "0":
                invoice.status = "0"
                messages.add_message(request, messages.INFO,
                                     "Status changed to REPORTER MUST APPROVE")
                invoice.save()
            elif "query_button" in request.POST and invoice.status != "1":
                invoice.status = "1"
                messages.add_message(request, messages.INFO,
                                     "Status changed to QUERIED BY REPORTER")
                invoice.save()
            elif "pay_button" in request.POST and invoice.status != "2":
                invoice.status = "2"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED BY REPORTER")
                invoice.save()
            elif "approve_button" in request.POST and invoice.status != "3":
                invoice.status = "3"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED BY EDITOR")
                invoice.save()
            elif "paid_button" in request.POST and invoice.status != "4":
                invoice.status = "4"
                messages.add_message(request, messages.INFO,
                                     "Status changed to PAID")
                invoice.save()
            elif "delete_button" in request.POST and invoice.status != "5":
                invoice.status = "5"
                messages.add_message(request, messages.INFO,
                                     "Status changed to DELETED")
                invoice.save()
            elif form.has_changed():
                messages.add_message(request, messages.INFO,
                                     "Details updated")
                invoice.save()
            if user.has_perm("payment.change_commission"):
                commissionformset = CommissionFormSet(request.POST,
                                                      request.FILES)
                if commissionformset.is_valid():
                    commissionformset.save()
        else:
            messages.add_message(request, messages.ERROR,
                                 "Please make corrections")
    else:
        if staff_view:
            form = forms.InvoiceStaffForm(request.POST or None,
                                          instance=invoice)
        else:
            if invoice.status == "-" or invoice.status == "5":
                raise Http404
            form = forms.InvoiceForm(request.POST or None, instance=invoice)

    if invoice.status == "0" or invoice.status == "1":
        can_edit = True

    # Get commissions
    formset = None
    can_edit_commissions = False
    if staff_view:
        commissions = models.Commission.objects.for_staff().\
                      filter(invoice=invoice)
        if user.has_perm("payment.change_commission"):
            can_edit_commissions = True
            formset = CommissionFormSet(queryset=commissions)
    else:
        commissions = models.Commission.objects.for_authors().\
                      filter(invoice=invoice)
    if formset:
        commissionformset = zip(commissions, formset)
    else:
        commissionformset = zip(commissions, range(len(commissions)))

    if print_view:
        can_edit = False
        can_edit_commissions = False
        staff_view = False

    return render(request, "payment/invoice_detail.html",
                  {'invoice': invoice,
                   'commissionformset': commissionformset,
                   'staff_view': staff_view,
                   'form': form,
                   'can_edit': can_edit,
                   'can_edit_commissions': can_edit_commissions,
                   'formset': formset,
                   'site': Site.objects.get_current(),
                   'print_view': print_view})


@login_required
def invoice_print(request, author_pk, invoice_num):
    return invoice_detail(request, author_pk, invoice_num, print_view=True)


@staff_member_required
def commission_detail(request, pk=None):
    if not request.user.has_perm("payment.change_commission"):
        raise Http404
    commission = None
    if request.method == 'POST':
        if pk:
            commission = get_object_or_404(models.Commission, pk=pk)
            form = forms.CommissionForm(request.POST, instance=commission)
        else:
            form = forms.CommissionForm(request.POST)
        if form.is_valid():
            author = form.cleaned_data['author']
            if pk is None:
                commission = form.save(commit=False)
                commission.sys_generated = False
                commission.date_generated = timezone.now()
                commission = form.save(commit=False)
                invoice = models.Invoice.get_open_invoice_for_author(author)
            else:
                current_commission = models.Commission.objects.get(pk=pk)
                if current_commission.invoice.author == author:
                    invoice = current_commission.invoice
                else:
                    invoice = models.Invoice.\
                              get_open_invoice_for_author(author)
                commission = form.save(commit=False)
            commission.invoice = invoice
            commission.save()

            pk = commission.pk
            messages.add_message(request, messages.INFO,
                                 "Commission saved")
    else:
        if pk:
            commission = models.Commission.objects.get(pk=pk)
            form = forms.CommissionForm(instance=commission)
            form.fields["author"].initial = commission.invoice.author.pk
        else:
            form = forms.CommissionForm()
            commission = None
            author_pk = request.GET.get("author", None)
            if author_pk:
                try:
                    author = get_object_or_404(Author, pk=int(author_pk))
                    form.fields["author"].initial = author.pk
                except:
                    pass
    return render(request, "payment/commission_detail.html",
                  {'form': form,
                   'pk': pk,
                   'commission': commission})
