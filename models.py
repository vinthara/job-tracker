from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

# Database setup
engine = create_engine('sqlite:///job_tracker.db', echo=False)
SessionLocal = sessionmaker(bind=engine)


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    company = Column(String, nullable=False)
    firstname = Column(String)
    lastname = Column(String)
    linkedin_link = Column(String)
    phone_number = Column(String)
    updated_date = Column(Date, nullable=False)


class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)  # Foreign key to contacts table
    client = Column(String)  # Final client you work with (e.g., Servier)
    job_link = Column(String)
    date = Column(Date, nullable=False)
    source = Column(String, nullable=False)
    status = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    answer_date = Column(Date)
    my_decision = Column(String, default='', nullable=False)  # Your decision: interested, accepted, declined, considering, backup
    expected_rate = Column(Float)
    offered_rate = Column(Float)
    duration = Column(String)
    start_date = Column(Date)
    notes = Column(String)
    closed = Column(String, default='no', nullable=False)

    # Relationship to access company name via contact
    contact = relationship("Contact", backref="applications")


class JobOffer(Base):
    __tablename__ = 'job_offers'

    id = Column(Integer, primary_key=True)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String)
    date_added = Column(Date, nullable=False)


def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)
