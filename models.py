from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func


db=SQLAlchemy()

class EscalationApproval(db.Model):
    __tablename__ = 'esclation_approval'
    
    escid = Column(String, primary_key=True, index=True)
    approval_id = Column(String, index=True)
    responder_name = Column(String)
    comments = Column(String)
    approval_status = Column(String)
    vendor_code = Column(String)

    def to_dict(self):
        """Returns a dictionary representation of the object."""
        return {
            'escid': self.escid,
            'approval_id': self.approval_id,
            'responder_name': self.responder_name,
            'comments': self.comments,
            'approval_status': self.approval_status,
            'vendor_code': self.vendor_code
        }
    
    def __repr__(self):
        return f"<EscalationApproval escid='{self.escid}', status='{self.approval_status}'>"



class EscalationApproval(Base):
    __tablename__ = "esclation_approval"

    escid = Column(String, primary_key=True, index=True)
    approval_id = Column(String, index=True)
    responder_name = Column(String)
    comments = Column(String)
    approval_status = Column(String)
    vendor_code = Column(String)


db = SQLAlchemy()  # Initialize SQLAlchemy instance

class EscalationApproval(db.Model):
    __tablename__ = 'esclation_approval'
    
    escid = Column(String(36), primary_key=True, index=True, server_default=func.gen_random_uuid())  # String for UUID
    approval_id = Column(String, index=True)
    responder_name = Column(String, index=True)
    comments = Column(String, index=True)
    approval_status = Column(String, index=True)
    vendor_code = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
