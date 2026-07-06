Start

Requester: MR
KTU: Approval KTU

IF Stock Available
    Warehouse: Internal transfer
    Warehouse: Send Requested Product 
    Requester: Receive Product 
    END
ELSE
    IF Approved
        Requester: Fill PR Form
        Requester: PR request approval
    ELSE
        GOTO MR
    ENDIF

    Approval 1: Approval 1
    IF Approved
    ELSE
        GOTO PR request approval
    ENDIF
    
    Approval 2: Approval 2
    IF Approved
    ELSE
        GOTO PR request approval
    ENDIF
    
    Procurement: Purchase Requisition Line Assign Buyer
    Procurement: Create RFQ from Purchase Requisition Line
    System: RFQ Created
    Procurement: Create Alternatives
    Procurement: Send RFQ to Vendor
    Vendor: Vendor Portal quantity, price filled
    Vendor: Save Changes in vendor Portal
    System: Quantity and Price Updated in Purchase Comparison
    Procurement: Select winner in Purchase Comparison
    Procurement: Ask Approval Purchase Comparison
    
    Approval 1: Approval 1
    IF Approved
    ELSE
        GOTO Select winner in Purchase Comparison
    ENDIF
    
    Approval 2: Approval 2
    IF Approved
    ELSE
        GOTO Select winner in Purchase Comparison
    ENDIF
    
    System: Winner RFQ Processed
    Procurement: Choose Payment Term[CBD]
    System: Payment Term Choosed CBD
    Procurement: Confirm RFQ to PO
    
    Approval 1: Approval 1
    IF Approved
    ELSE
        GOTO Winner RFQ Processed
    ENDIF
    
    Approval 2: Approval 2
    IF Approved
    ELSE
        GOTO Winner RFQ Processed
    ENDIF
    
    System: PO Confirmed
    Procurement: Click Create Vendor Payment
    Finance: Process Vendor Payment
    Finance: Process Vendor Bill
    Warehouse: Receipt Goods

ENDIF

End
