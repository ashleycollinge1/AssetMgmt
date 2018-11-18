from app import db


class Asset(db.Model):
    """
    Every asset managed by the system has a record in here, which contains the
    very basic information, the same for every asset. Then there are different
    asset types which are managed, e.g. Asset_PC and Asset_Monitor.
    """
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    status = db.Column(db.String)
    serialnumber = db.Column(db.String, unique=True)
    purchaseordernumber = db.Column(db.String)
    asset_type = db.Column(db.String)
    assetpcrecord = db.relationship('AssetPC', backref='asset', lazy=True)


class WindowsAgent(db.Model):
    """
    Every windows pc runs an agent service which is what reports back all of the
    information for the asset
    """
    id = db.Column(db.Integer, primary_key=True)
    agent_version = db.Column(db.Integer)
    asset_pc_id = db.Column(db.Integer, db.ForeignKey('assetpc.id'), nullable=False)


class AssetPC(db.Model):
    """
    This contains records for all PC assets held in the estate. Each record
    has a relationship with the Asset ID in [dbo].[Asset]. This makes it easier
    when it comes to taking the machine off the domain; it still exists as an
    asset and needs to be managed - separate from the domain.
    """
    __tablename__ = "assetpc"
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    hostname = db.Column(db.String)
    domain = db.Column(db.String)
    operating_system = db.Column(db.String)
    service_pack_version = db.Column(db.String)
    last_bootup_time = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime, default=db.func.current_timestamp())
    manufacturer = db.Column(db.String)
    model = db.Column(db.String)
    memorygb = db.Column(db.Integer)
    cpu_maxclockspeed = db.Column(db.Float)
    cpu_logicalcorecount = db.Column(db.Integer)
    cpu_physicalcorecount = db.Column(db.Integer)
    cpu_model = db.Column(db.String)
    physical_arch = db.Column(db.String)
    windows_agent = db.relationship('WindowsAgent', backref='assetpc', lazy=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    network_interfaces = db.relationship('Asset_PC_NetInt', backref='assetpc', lazy=True)


class Asset_Location(db.Model):
    """
    Record for each location that can exist for an Asset to be stored.
    Can add notes for each location.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    notes = db.Column(db.String)


class Asset_Category(db.Model):
    """
    Different categories to assign to each asset.
    Can be created by users
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Asset_PC_NetInt(db.Model):
    """
    Record for each network interface on each PC
    """
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String)
    mac_address = db.Column(db.String)
    subnet_mask = db.Column(db.String)
    gateway = db.Column(db.String)
    asset_pc_id = db.Column(db.Integer, db.ForeignKey('assetpc.id'), nullable=False)


"""
class Asset_PC_PhysDisk(db.Model):
    #Record for each physical disk on each PC
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String)
    freespace = db.Column(db.Integer)
    totalsize = db.Column(db.Integer)
    mediatype = db.Column(db.String)
    status = db.Column(db.String)
    asset_pc_id =

class Asset_PC_LogDisk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String)
    freespace = db.Column(db.Integer)
    totalsize = db.Column(db.Integer)
    filesystem = db.Column(db.String)
    mediatype = db.Column(db.String)
    partition_type = db.Column(db.String)
    asset_pc_id

class Asset_PC_Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    displayname = db.Column(db.String)
    version = db.Column(db.String)
    uninstall_command = db.Column(db.String)
    publisher = db.Column(db.String)
    asset_pc_id =

class Asset_PC_Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    department = db.Column(db.String)
    asset_pc_id =
    """
