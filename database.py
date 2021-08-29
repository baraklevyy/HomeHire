from sqlalchemy import Table, Column, String, Integer, MetaData, func, delete, update


################################
#      DATABASE FUNCTIONS      #
################################



# Function used to create a postgreSQL table.
def listings_table(db):
    table = Table('listings', MetaData(db),
                  Column('renter', String, nullable=False),
                  Column('streetAddress', String, nullable=False),
                  Column('description', String),
                  Column('imageUrl', String),
                  Column('transactionUrl', String)
                  )
    return table

# Function used to add new property listing to the table.
def add_listing(listings_table, renter, streetAddress, description, imageUrl, transactionUrl):
    listings_table.insert().values(renter=renter, streetAddress=streetAddress, description=description,
                                imageUrl=imageUrl, transactionUrl=transactionUrl).execute()

# Function used to delete row from the DataBase. Each tenant can attain only one property so the deletion will be One-to-one relation.
def delete_listing(listings_table, renter):
    delete(listings_table).where(listings_table.c.renter == renter).execute()

# Function used to update the Testnet (Kovan/Ropsten) transation URL.
def update_transaction_url(listings_table, renter, transactionUrl):
    listings_table.update().where(renter=renter).values(transactionUrl=transactionUrl).execute().fetchall()

# Function used to update the tenant address in the database table.
def update_renter(listings_table, old_renter, new_renter):
    update(listings_table).where(listings_table.c.renter == old_renter).values(renter=new_renter).execute()

# Getter function used to retreive the available listings.
def get_listings(listings_table):
    select_statement = listings_table.select().execute()
    result_set = select_statement.fetchall()
    listings = []
    for r in result_set:
        listings.append(r)
        print(r)
    return listings

# Getter function used to retrieve specific property given tenant address (one-to-one relation).
def get_listing(listings_table, renter):
    select_statement = listings_table.select().where(listings_table.c.renter==renter).execute()
    listing = select_statement.fetchone()
    return listing