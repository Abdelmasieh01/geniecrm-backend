from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Lead, Stage
from .serializers import LeadSerializer, StageSerializer

@api_view(['GET'])
def get_leads(request, lead_id=None):
    if lead_id:
        try:
            lead = Lead.objects.get(id=lead_id)
            serializer = LeadSerializer(lead)
        except Lead.DoesNotExist:
            return Response({"error": "Lead not found"}, status=404)
    else:
        leads = Lead.objects.all()
        serializer = LeadSerializer(leads, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_stages_with_leads(request):
    stages = Stage.objects.prefetch_related('leads')  # Optimize query
    serializer = StageSerializer(stages, many=True)
    return Response(serializer.data)
