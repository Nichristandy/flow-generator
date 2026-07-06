Start

Requester: Create Material Request (MR)

KTU: Review Material Request

IF Approved

    Requester: Submit Purchase Requisition (PR)
    Approval 1: Approve Purchase Requisition
    Approval 2: Approve Purchase Requisition

    Procurement: Assign Buyer to Purchase Requisition Line
    Buyer: Create RFQ from Purchase Requisition Line

    Procurement: Create RFQ Alternatives
    Procurement: Send RFQ to Vendor

    Vendor: Fill Quantity and Price in Vendor Portal
    Vendor: Save Vendor Portal Changes

    Procurement: Review Updated Purchase Comparison
    Procurement: Select Winner

    Procurement: Request Purchase Comparison Approval
    Approval 1: Approve Purchase Comparison
    Approval 2: Approve Purchase Comparison

    Procurement: Process Winner RFQ
    Procurement: Choose Payment Term

    IF Cash Before Delivery (CBD)

        Procurement: Confirm RFQ to Purchase Order

        Approval 1: Approve Purchase Order

        IF Approval 1 Rejected
            Procurement: Revise Purchase Order
            Procurement: Confirm RFQ to Purchase Order
            Approval 1: Approve Purchase Order
        ENDIF

        Approval 2: Approve Purchase Order

        IF Approval 2 Rejected
            Procurement: Revise Purchase Order
            Procurement: Confirm RFQ to Purchase Order
            Approval 1: Approve Purchase Order
            Approval 2: Approve Purchase Order
        ENDIF

        Procurement: Purchase Order Confirmed

        Procurement: Create Vendor Payment
        Finance: Process Vendor Payment
        Finance: Process Vendor Bill
        Warehouse: Receive Goods

    ELSE

        Procurement: Confirm RFQ to Purchase Order

        Approval 1: Approve Purchase Order

        IF Approval 1 Rejected
            Procurement: Revise Purchase Order
            Procurement: Confirm RFQ to Purchase Order
            Approval 1: Approve Purchase Order
        ENDIF

        Approval 2: Approve Purchase Order

        IF Approval 2 Rejected
            Procurement: Revise Purchase Order
            Procurement: Confirm RFQ to Purchase Order
            Approval 1: Approve Purchase Order
            Approval 2: Approve Purchase Order
        ENDIF

        Procurement: Purchase Order Confirmed

        Warehouse: Receive Goods
        Finance: Process Vendor Bill
        Finance: Process Vendor Payment

    ENDIF

ELSE

    Requester: Revise Material Request

ENDIF

End