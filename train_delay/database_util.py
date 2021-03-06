from .models import TrainInfo, LocalStorage
from datetime import timedelta, datetime
from .util import *

patch_data = {"Seibu":"西武鉄道各線", "Keisei":"京成線", "Keikyu":"京急線", "Keio":"京王線"}

def refresh_database():
    operator_data = read_data('Operator')
    railway_data = read_data('Railway')
    train_info_data = read_data('TrainInformation')

    checkpoint = LocalStorage()
    checkpoint.last_update = timezone.now()
    checkpoint.save()

    TrainInfo.objects.all().delete()

    for data in train_info_data:
        train_info = TrainInfo()
        operator_tag = data["odpt:operator"]
        operator = retreive_exact(operator_data, lambda x: x["owl:sameAs"] == operator_tag)
        railway_ja, railway_en = "", ""
        try:
            railway_tag = data["odpt:railway"]
            railway = retreive_exact(railway_data, lambda x: x["owl:sameAs"] == railway_tag)
            railway_ja = railway["odpt:railwayTitle"]["ja"]
            railway_en = railway["odpt:railwayTitle"]["en"]
        except:
            railway_en = name_extractor(data["owl:sameAs"][22:])
            railway_ja = patch_data[railway_en]
        side_data = {
            "operator_en": operator["odpt:operatorTitle"]["en"],
            "operator_ja": operator["odpt:operatorTitle"]["ja"],
            "railway_en": railway_en,
            "railway_ja": railway_ja,
        }
        train_info.update_train(data, side_data)

def check_last_update():
    checkpoint = (LocalStorage.objects.all())[0]
    current_datetime = timezone.now()

    # The interval is 2 minutes
    if current_datetime - checkpoint.last_update > timedelta(minutes=2):
        refresh_database()
        return True
    
    else:
        return False