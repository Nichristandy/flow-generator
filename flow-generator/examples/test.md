Start

Requester: Create Material Request
KTU: Review Material Request

IF Approved
    Requester: Submit Purchase Requisition Request
ELSE
    Requester: Revise Material Request
ENDIF

Requester: Request Purchase Requisition Approval

Approval 1: Review Purchase Requisition

IF Approved
    Approval 2: Review Purchase Requisition
ELSE
    Requester: Revise Purchase Requisition
ENDIF

IF Approved
    Procurement: Assign Buyer
ELSE
    Requester: Revise Purchase Requisition
ENDIF

Procurement: Create RFQ from Purchase Requisition Line
Procurement: RFQ Created
Procurement: Create Alternative Quotations
Procurement: Send RFQ to Vendor

Vendor: Fill Quantity and Price in Vendor Portal
Vendor: Save Vendor Portal Changes

Procurement: Purchase Comparison Updated
Procurement: Select Winner
Procurement: Request Purchase Comparison Approval

Approval 1: Review Purchase Comparison

IF Approved
    Approval 2: Review Purchase Comparison
ELSE
    Procurement: Revise Purchase Comparison
ENDIF

IF Approved
    Procurement: Process Winner RFQ
ELSE
    Procurement: Revise Purchase Comparison
ENDIF

Procurement: Choose Payment Term

IF Down Payment
    Procurement: Fill Down Payment Percentage
ENDIF

Procurement: Request RFQ Approval

Approval 1: Review RFQ

IF Approved
    Approval 2: Review RFQ
ELSE
    Procurement: Revise RFQ
ENDIF

IF Approved
    Procurement: Confirm RFQ to Purchase Order
ELSE
    Procurement: Revise RFQ
ENDIF

Approval 1: Review Purchase Order

IF Approved
    Approval 2: Review Purchase Order
ELSE
    Procurement: Revise Purchase Order
ENDIF

IF Approved
    Procurement: Purchase Order Confirmed
ELSE
    Procurement: Revise Purchase Order
ENDIF

Procurement: Create Vendor Down Payment
Finance: Process Vendor Down Payment
Finance: Process Vendor Bill
Inventory: Receive Goods
Finance: Process Final Vendor Payment

End