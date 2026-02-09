from models import db, EscalationApproval
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Optional, List

# Define a custom exception for service layer errors
class EscalationServiceError(Exception):
    """Custom exception for errors in the Escalation Service layer."""
    pass

def create_escalation(data: Dict) -> EscalationApproval:
    """
    Creates a new EscalationApproval record in the database.

    :param data: Dictionary containing the record data.
    :return: The newly created EscalationApproval object.
    :raises EscalationServiceError: If a database error occurs.
    """
    if not data or 'escid' not in data:
        raise ValueError("Missing data or 'escid' field.")

    try:
        new_record = EscalationApproval(**data)

        db.session.add(new_record)
        db.session.commit()
        return new_record
    
    except SQLAlchemyError as e:
        db.session.rollback()
        # Log the error (in a real app) and raise a service-specific exception
        raise EscalationServiceError(f'Database error during creation: {e}')
    
    
    
    except Exception as e:
        db.session.rollback()
        raise EscalationServiceError(f'Unexpected error during creation: {e}')


def get_all_escalations() -> List[EscalationApproval]:
    """
    Retrieves all EscalationApproval records.

    :return: A list of EscalationApproval objects.
    """
    return EscalationApproval.query.all()


def get_escalation_by_id(escid: str) -> Optional[EscalationApproval]:
    """
    Retrieves a single EscalationApproval record by its escid.

    :param escid: The unique identifier of the escalation.
    :return: The EscalationApproval object or None if not found.
    """
    return EscalationApproval.query.get(escid)


def update_escalation(escid: str, data: Dict) -> Optional[EscalationApproval]:
    """
    Updates an existing EscalationApproval record.

    :param escid: The unique identifier of the escalation to update.
    :param data: Dictionary containing the fields to update.
    :return: The updated EscalationApproval object or None if not found.
    :raises EscalationServiceError: If a database error occurs.
    """
    record = EscalationApproval.query.get(escid)
    if not record:
        return None  # Indicate that the record was not found

    try:
        # Update fields only if they are present in the request data
        record.approval_id = data.get('approval_id', record.approval_id)
        record.responder_name = data.get('responder_name', record.responder_name)
        record.comments = data.get('comments', record.comments)
        record.approval_status = data.get('approval_status', record.approval_status)
        record.vendor_code = data.get('vendor_code', record.vendor_code)

        db.session.commit()
        return record
    
    
    except SQLAlchemyError as e:
        db.session.rollback()
        raise EscalationServiceError(f'Database error during update: {e}')
    except Exception as e:
        db.session.rollback()
        raise EscalationServiceError(f'Unexpected error during update: {e}')


def delete_escalation(escid: str) -> bool:
    """
    Deletes an EscalationApproval record by its escid.

    :param escid: The unique identifier of the escalation to delete.
    :return: True if the record was found and deleted, False otherwise.
    :raises EscalationServiceError: If a database error occurs.
    """
    record = EscalationApproval.query.get(escid)
    if not record:
        return False  # Indicate that the record was not found

    try:
        db.session.delete(record)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        raise EscalationServiceError(f'Database error during deletion: {e}')
    except Exception as e:
        db.session.rollback()
        raise EscalationServiceError(f'Unexpected error during deletion: {e}')

