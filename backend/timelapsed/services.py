#Add in services/functionality here

from .models import Users, Topic, Date_Range, Card, Subclass, Card_Relationship_Move_Action, Card_Relationship_Delete_Action, Card_Relationship_Subclass_Action, Card_Relationship_In_Same_Action, Subclass_Relationships, Card_Relationship_Parent_Action, Card_Relationship_Child_Action
from collections import OrderedDict 
from .batching.responses import card_response_builder

def get_user_information(data):

  test = [i for i in Topic.objects.values('Name', 'id').filter(Email = data['Email']).order_by('Position') ]

  arr = []

  arr.append


  for i in test:
    cards = [i for i in Card.objects.values('Name', 'Description', 'id' ).filter(Topic = i['id']).order_by('Position')]
    for j in cards:
      times = [j for j in Date_Range.objects.values('id', 'Day', 'Begin_Date', 'Num_Weeks', 'Weeks_Skipped', 'Begin_Time', 'End_Time').filter(Card_ID = Card.objects.get(id = j['id'])).order_by('Begin_Date') ]
      j['Times'] = times

    arr.append( {'Data' : {'id': i['id'], 'Name': i['Name'], 'Cards': cards}} )
    

  return arr


def create_parent_relationship(data, user):

  #Relationship just signifies parent or child. 

  res = {}

  if 'Move' in data:

    move_topic = Topic.objects.get(id = data['Move']['Topic_ID'])
    move_card = Card.objects.get(id = data['Move']['Card_ID'])

    res['id'] = Card_Relationship_Parent_Action.objects.create(Parent_ID = move_card, Email = Users.objects.get(Email = user), Move_ID = Card_Relationship_Move_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = move_card, Topic_ID = move_topic )).id
  
    res['str'] = f'{move_card.Name} is moved to {move_topic.Name}'

    return res


  if 'Same' in data:
    same_card = Card.objects.get(id = data['Same']['Card_ID'])
    same_child = Card.objects.get(id = data['Same']['Child_ID'])


    res['id'] = Card_Relationship_Parent_Action.objects.create(Parent_ID = same_card, Email = Users.objects.get(Email = user), Same_ID = Card_Relationship_In_Same_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = same_card, Child_ID = same_child )).id
    
    res['str'] = f'{same_card.Name} must be in the same topic as {same_child.Name}'

    return res

  if 'Delete' in data:
    delete_card = Card.objects.get(id = data['Delete']['Card_ID'])


    res['id'] = Card_Relationship_Parent_Action.objects.create(Parent_ID = delete_card, Email = Users.objects.get(Email = user), Delete_ID = Card_Relationship_Delete_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = delete_card )).id

    res['str'] = f'{delete_card.Name} is deleted'

    return res

  if 'Subclass' in data:


    subclass_card = Card.objects.get(id = data['Subclass']['Card_ID'])
    subclass = Subclass.objects.get(id = data['Subclass']['Subclass_ID'])


    res['id'] = Card_Relationship_Parent_Action.objects.create(Parent_ID = subclass_card, Email = Users.objects.get(Email = user), Subclass_ID = Card_Relationship_Subclass_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = subclass_card, Subclass_ID = subclass )).id
    res['str'] = f'{subclass_card.Name} is added to subclass on card {subclass.Head.Name}'

    return res



def create_child_relationship(data, parent_id, user):

  #Relationship just signifies parent or child. 

  res = {}

  parent = Card_Relationship_Parent_Action.objects.get(id = parent_id)

  if 'Move' in data:

    move_topic = Topic.objects.get(id = data['Move']['Topic_ID'])
    move_card = Card.objects.get(id = data['Move']['Card_ID'])

    res['id'] = Card_Relationship_Child_Action.objects.create(Parent_Action = parent, Child_ID = move_card,Email = Users.objects.get(Email = user), Move_ID = Card_Relationship_Move_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = move_card, Topic_ID = move_topic )).id
    res['str'] = f'{move_card.Name} is moved to {move_topic.Name}'

    return res


  if 'Same' in data:
    same_card = Card.objects.get(id = data['Same']['Card_ID'])
    same_child = Card.objects.get(id = data['Same']['Child_ID'])

    res['id'] = Card_Relationship_Child_Action.objects.create(Parent_Action = parent, Child_ID = same_card, Email = Users.objects.get(Email = user), Same_ID = Card_Relationship_In_Same_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = move_card, Child_ID = same_child )).id  
    res['str'] = f'{same_card.Name} must be in the same topic as {same_child.Name}'

    return res

  if 'Delete' in data:
    delete_card = Card.objects.get(id = data['Delete']['Card_ID'])

    res['id'] = Card_Relationship_Child_Action.objects.create(Parent_Action = parent, Child_ID = delete_card,Email = Users.objects.get(Email = user), Delete_ID = Card_Relationship_Delete_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = delete_card )).id

    res['str'] = f'{delete_card.Name} is deleted'

    return res

  if 'Subclass' in data:


    subclass_card = Card.objects.get(id = data['Subclass']['Card_ID'])
    subclass = Subclass.objects.get(id = data['Subclass']['Subclass_ID'])


    res['id'] = Card_Relationship_Child_Action.objects.create(Parent_Action = parent, Child_ID = subclass_card, Email = Users.objects.get(Email = user), Subclass_ID = Card_Relationship_Subclass_Action.objects.create(Email = Users.objects.get(Email = user), Card_ID = subclass_card, Subclass_ID = subclass )).id

    res['str'] = f'{subclass_card.Name} is added to subclass on card {subclass.Head.Name}'

    return res    