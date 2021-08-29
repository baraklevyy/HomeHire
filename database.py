from sqlalchemy import Table, Column, String, Integer, MetaData, func, delete, update


def listings_table(db):
    table = Table('listings', MetaData(db),
                  Column('renter', String, nullable=False),
                  Column('streetAddress', String, nullable=False),
                  Column('description', String),
                  Column('imageUrl', String),
                  Column('transactionUrl', String)
                  )
    return table


def add_listing(listings_table, renter, streetAddress, description, imageUrl, transactionUrl):
    listings_table.insert().values(renter=renter, streetAddress=streetAddress, description=description,
                                imageUrl=imageUrl, transactionUrl=transactionUrl).execute()

"""
delete row from the DataBase. Each renter can attain only one property so the deletion will be One-to-one function.
"""
def delete_listing(listings_table, renter):
    # listings_table.delete().returning(listings_table.c.row).\
    # where(listings_table.c.renter==renter).execute()

    delete(listings_table).where(listings_table.c.renter == renter).execute()

def update_transaction_url(listings_table, renter, transactionUrl):
    listings_table.update().where(renter=renter).values(transactionUrl=transactionUrl).execute().fetchall()

def update_renter(listings_table, old_renter, new_renter):
    update(listings_table).where(listings_table.c.renter == old_renter).values(renter=new_renter).execute()

def get_listings(listings_table):
    select_statement = listings_table.select().execute()
    result_set = select_statement.fetchall()
    listings = []
    for r in result_set:
        listings.append(r)
        print(r)
    return listings


def get_listing(listings_table, renter):
    select_statement = listings_table.select().where(listings_table.c.renter==renter).execute()
    listing = select_statement.fetchone()
    return listing