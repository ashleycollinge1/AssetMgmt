from app import db

class Asset(db.Model):
    asset_id      = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
    computer_name
    status
    domain
    location_id
    serialnumber
    purchaseordernumber



location_id
name


tables of info

//network info
net_int_id
ip_address
mac_address
subnet_mask
gateway
asset_id

//disk info
physical_disk_id
caption
freespace
totalsize
mediatype
status

logical_disk_id
caption
freespace
physical_disk_id
totalsize
filesystem
mediatype
partition_type

//software
software_id
displayname
version
uninstall_command
publisher
asset_id

//users
user_id
username
department
