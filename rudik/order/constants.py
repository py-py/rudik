from django.utils.translation import ugettext_lazy as _

PAYMENT_TYPE_BANK_CARD = 1
PAYMENT_TYPE_CASH_ON_DELIVERY = 2

PAYMENT_TYPES = (
    (PAYMENT_TYPE_BANK_CARD, _("Bank card")),
    (PAYMENT_TYPE_CASH_ON_DELIVERY, _("Cash on delivery")),
)

DELIVERY_COMPANY_NOVAPOSHTA = 1
DELIVERY_COMPANY_UKRPOSHTA = 2

DELIVERY_COMPANIES = (
    (DELIVERY_COMPANY_NOVAPOSHTA, _("Nova Poshta")),
    (DELIVERY_COMPANY_UKRPOSHTA, _("UkrPoshta")),
)

DELIVERY_COMPANY_BRANCH = 1
DELIVERY_COMPANY_CURRIER = 2

DELIVERY_TYPES = (
    (DELIVERY_COMPANY_BRANCH, _("Branch")),
    (DELIVERY_COMPANY_CURRIER, _("Currier")),
)

STATUS_NEW = 1
STATUS_COULD_NOT_CALL = 2
STATUS_APPROVED = 3
STATUS_WAIT_FOR_PAYMENT = 4
STATUS_COMPLETED = 5
STATUS_PAID = 6
STATUS_CANCELED = 7
STATUS_RETURNED = 8

STATUSES = (
    (STATUS_NEW, _("New")),
    (STATUS_COULD_NOT_CALL, _("Didn't call")),
    (STATUS_APPROVED, _("Approved")),
    (STATUS_WAIT_FOR_PAYMENT, _("Wait for payment")),
    (STATUS_COMPLETED, _("Completed")),
    (STATUS_PAID, _("Paid")),
    (STATUS_CANCELED, _("Canceled")),
    (STATUS_RETURNED, _("Returned")),
)

NOTIFICATION_TYPE_SMS = 1
NOTIFICATION_TYPE_EMAIL = 2

NOTIFICATION_TYPES = ((NOTIFICATION_TYPE_SMS, _("SMS")), (NOTIFICATION_TYPE_EMAIL, _("Email")))
