import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Lead, Stage
from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError


class CRMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'kanban_updates'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')
        print(event_type)

        try:
            if event_type == 'create_lead':
                await self.create_lead(data)
            if event_type == 'update_lead':
                await self.update_lead(data)
            if event_type == 'move_lead':
                await self.move_lead(data)
        except IntegrityError:
            await self.send(text_data=json.dumps({
                "type": "error", "message": "Error in email field."
            }))

    async def create_lead(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        notes = data.get('notes')

        # Get or create the default "New" stage; get_or_create returns (instance, created)
        stage, _ = await sync_to_async(Stage.objects.get_or_create)(
            name="New", order=1
        )

        # Create a new Lead instance using the correct model
        lead = Lead(first_name=first_name, last_name=last_name,
                    email=email, phone=phone, notes=notes, stage=stage)
        await sync_to_async(lead.save)()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'lead_created',
                'lead': {
                    'id': lead.id,
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'email': lead.email,
                    'phone': lead.phone,
                    'notes': lead.notes,
                    'stage_id': lead.stage.id,
                }
            }
        )



    async def update_lead(self, data):
        lead_id = data.get("lead_id")
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        notes = data.get('notes')

        #  Get the lead and update it
        lead = await sync_to_async(Lead.objects.select_related("stage").get)(id=lead_id)
        lead.first_name = first_name
        lead.last_name = last_name
        lead.email = email
        lead.phone = phone
        lead.notes = notes
        await sync_to_async(lead.save)()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'lead_updated',
                'lead': {
                    'id': lead.id,
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'email': lead.email,
                    'phone': lead.phone,
                    'notes': lead.notes,
                    'stage_id': lead.stage.id,
                }
            }
        )

    async def move_lead(self, data):
        lead_id = data.get('lead_id')
        new_stage_id = data.get('new_stage_id')

        lead = await sync_to_async(Lead.objects.select_related("stage").get)(id=lead_id)
        old_stage = lead.stage
        new_stage = await sync_to_async(Stage.objects.get)(id=new_stage_id)
        lead.stage = new_stage
        await sync_to_async(lead.save)()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'lead_moved',
                'lead': {
                    'id': lead.id,
                    'old_stage_id': old_stage.id,
                    'new_stage_id': new_stage.id,
                }
            }
        )

    async def lead_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'lead_created', 
            'lead': event['lead']
        }))

    async def lead_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'lead_updated',
            'lead': event['lead']
        }))

    async def lead_moved(self, event):
        await self.send(text_data=json.dumps({
            'type': 'lead_moved',
            'lead': event['lead']
        }))
