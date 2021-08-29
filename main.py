import re
from fastapi import Depends, FastAPI, HTTPException, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm, OAuth2, HTTPBasic
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, Response, JSONResponse, HTMLResponse, FileResponse
from starlette.requests import Request
from pydantic.decorator import Optional

import transactions
import config
from database import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import inspect

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Postgres
db = create_engine(config.DB_STRING)
conn = db.connect()
session = Session(db)
table = listings_table(db)

# create table if it does not already exist
if not inspect(db).has_table('listings'):
    print('\'listings\' table does not yet exist. Creating it now...')
    table.create()

# route to home page
@app.route("/", methods=["GET", "POST"])
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# route to managment page
@app.get("/managment", response_class=HTMLResponse)
async def managment(request: Request):
    return templates.TemplateResponse("managment.html", {"request": request})

# commit addLandlord transaction
@app.post("/managment/add")
async def add_landlord_confirm(request: Request, landlord: str = Form(...)):
    txn_dict = transactions.addLandlord(landlord)
    return templates.TemplateResponse("confirm_add_landlord.html", {"request": request, "txn_data": txn_dict['data'],
                                                                   "contract_address": config.CONTRACT_ADDRESS,
                                                                    "landlord": landlord})
# commit delete home from contract transaction                                                                   
@app.post("/managment/delete")
async def delete_home_confirm(request: Request, renter: str = Form(...)):
    txn_dict = transactions.deleteHome(renter)
    return templates.TemplateResponse("confirm_delete_home.html", {"request": request, "txn_data": txn_dict['data'],
                                                                "contract_address": config.CONTRACT_ADDRESS,
                                                                    "renter": renter})
# commit delete home from DB                                                                     
@app.post("/managment/deleteDB")
async def deleteDB_home_confirm(request: Request, renter: str = Form(...), pwd: str = Form(...)):
    if(pwd == "barakandonnforever"):
        delete_listing(table, renter)
    return templates.TemplateResponse("index.html", {"request": request})

# commit change renter transaction 
@app.post("/managment/chngRenter")
async def change_renter_confirm(request: Request, oldRenter: str = Form(...), newRenter: str = Form(...), dateOfStart: str = Form(...), dateOfEnd: str = Form(...),  monthsToPay: str = Form(...)):
    txn_dict = transactions.changeRenter(oldRenter, newRenter, dateOfStart, dateOfEnd, monthsToPay)
    update_renter(table, oldRenter, newRenter)
    return templates.TemplateResponse("confirm_change_renter.html", {"request": request, "txn_data": txn_dict['data'],
                                                                   "contract_address": config.CONTRACT_ADDRESS,
                                                                    "oldRenter": oldRenter, "newRenter": newRenter,
                                                                    "dateOfStart": dateOfStart, "dateOfEnd": dateOfEnd})

# commit change rent transaction                                                                     
@app.post("/managment/chngRent")
async def change_rent_confirm(request: Request, renter: str = Form(...), newHomeRent: str = Form(...)):
    txn_dict = transactions.changeHomeRent(renter, int(newHomeRent),)
    return templates.TemplateResponse("confirm_change_rent.html", {"request": request, "txn_data": txn_dict['data'],
                                                                   "contract_address": config.CONTRACT_ADDRESS,
                                                                    "renter": renter, "newHomeRent": newHomeRent})
# route to connect wallet page
@app.get("/wallet", response_class=HTMLResponse)
async def connct_wallet(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# route to pay rent page
@app.get("/rent", response_class=HTMLResponse)
async def pay_rent_page(request: Request):
    return templates.TemplateResponse("pay_rent.html", {"request": request})

# commit pay rent transaction  
@app.post("/rent/pay")
async def pay_rent_confirm(request: Request, amount_wei: str = Form(...), landlord: str = Form(...)):
    txn_dict = transactions.payRent(landlord, amount_wei)
    return templates.TemplateResponse("confirm_transaction.html", {"request": request, "txn_data": txn_dict['data'],
                                                                   "contract_address": config.CONTRACT_ADDRESS,
                                                                   "amount_wei": amount_wei, "value": hex(txn_dict['value']),
                                                                   "landlord": landlord})

# commit wei_to_ethereum function  
@app.post("/rent/calc")
async def calc_wei(request: Request, amount_wei: str = Form(...)):
    calc = transactions.wei_to_ethereum(amount_wei)
    return templates.TemplateResponse("calc.html", {"request": request,
                                                                   "contract_address": config.CONTRACT_ADDRESS,
                                                                   "calc": calc})

# route to listings page
@app.route("/listings", methods=["GET", "POST"])
async def view_listings(request: Request):
    listings = get_listings(table)
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings})

# route to create new listing page
@app.get("/listings/new", response_class=HTMLResponse)
async def new_listing(request: Request):
    return templates.TemplateResponse("new_listing.html", {"request": request})

# commit add home transaction 
@app.post("/listings/new/post")
async def new_listing_post(request: Request, renter: str = Form(...), streetAddress: str = Form(...), description: str = Form(...),
                           imageUrl: str = Form(...), homeRent: str = Form(...), monthsToPay: str = Form(...), dateOfStart: str = Form(...), dateOfEnd: str = Form(...), garage: str = Form(...), elevator: str = Form(...), roomNum: str = Form(...)):
    txn_dict = transactions.addHome(int(homeRent), int(monthsToPay), renter, dateOfStart, dateOfEnd, elevator, garage, int(roomNum))
    add_listing(table, renter, streetAddress, description, imageUrl, None)
    return templates.TemplateResponse("confirm_new_home.html", {"request": request, "txn_data": txn_dict['data'],
                                                                "contract_address": config.CONTRACT_ADDRESS,
                                                                "renter": renter, "homeRent": homeRent,
                                                                "roomNum": roomNum, "monthsToPay": monthsToPay,
                                                                "dateOfStart": dateOfStart, "dateOfEnd": dateOfEnd,
                                                                "garage": garage, "elevator": elevator
                                                                })

# route to view a listing
@app.post("/listings/{renter}/post")
async def view_listing_post(renter, txn_hash: str = Form(...)):
    if txn_hash:
        transactionUrl =   'https://kovan.etherscan.io/tx/' + txn_hash
        update_transaction_url(table, renter, transactionUrl)
    listing = get_listing(table, renter)
    blockchain_data = transactions.getHome(renter)
    return templates.TemplateResponse("view_listing.html", {"request": request, "listing": listing, "blockchain_data": blockchain_data})


@app.get("/listings/{renter}", response_class=HTMLResponse)
async def view_listing(request: Request, renter):
    listing = get_listing(table, renter)
    blockchain_data = transactions.getHome(renter)
    return templates.TemplateResponse("view_listing.html", {"request": request, "listing": listing, "blockchain_data": blockchain_data})
