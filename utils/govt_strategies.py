import requests
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

def get_disaster_strategies(disaster_type):
    """
    Get government strategies and response guidelines for a specific disaster type
    Using ReliefWeb API to fetch relevant documents and reports
    
    Args:
        disaster_type: Type of disaster (e.g., Flood, Cyclone)
        
    Returns:
        list: Strategies and guidelines for the disaster type
    """
    # Normalize disaster type for API query
    disaster_type_query = disaster_type.lower()
    
    # First try to get strategies from ReliefWeb API
    try:
        reliefweb_strategies = get_reliefweb_strategies(disaster_type_query)
        
        # If we got meaningful strategies, return them
        if reliefweb_strategies and len(reliefweb_strategies) > 0:
            # Add default strategies to the beginning
            return get_default_strategies(disaster_type) + reliefweb_strategies
        
        # If no strategies found from API, fall back to default strategies
        return get_default_strategies(disaster_type)
    
    except Exception as e:
        logger.error(f"Error fetching government strategies: {str(e)}")
        # Fall back to default strategies on error
        return get_default_strategies(disaster_type)

def get_reliefweb_strategies(disaster_type_query):
    """
    Fetch disaster response strategies from ReliefWeb API
    """
    url = "https://api.reliefweb.int/v1/reports"
    params = {
        "appname": "climate-disaster-app",
        "profile": "list",
        "preset": "latest",
        "slim": 1,
        "query[value]": f"primary_country.name:India AND disaster_type:{disaster_type_query} AND format:guidelines",
        "limit": 10
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        strategies = []
        for item in data.get("data", []):
            fields = item.get("fields", {})
            
            # Extract relevant information
            strategy = {
                "title": fields.get("title"),
                "body": fields.get("body", ""),
                "date": fields.get("date", {}).get("created"),
                "source": fields.get("source", [{}])[0].get("name") if fields.get("source") else "ReliefWeb",
                "url": fields.get("url"),
                "file_url": fields.get("file", [{}])[0].get("url") if fields.get("file") else None,
                "type": "guideline",
                "from_api": True
            }
            
            strategies.append(strategy)
        
        return strategies
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching strategies from ReliefWeb API: {str(e)}")
        raise Exception(f"Failed to fetch strategies from ReliefWeb: {str(e)}")

def get_default_strategies(disaster_type):
    """
    Provide default government strategies for different disaster types
    Used as fallback when API data is unavailable
    """
    # Common phases of disaster management
    phases = ["Preparedness", "Response", "Recovery", "Mitigation"]
    
    # Default strategies for different disaster types
    strategies = {
        "Flood": [
            {
                "title": "National Flood Response Protocol",
                "body": "The National Disaster Management Authority (NDMA) recommends immediate evacuation of low-lying areas, deployment of NDRF teams, and establishment of relief camps with essential supplies. State governments should activate District Disaster Management Authorities (DDMAs) to coordinate local response.",
                "phase": "Response",
                "authority": "National Disaster Management Authority (NDMA)"
            },
            {
                "title": "Flood Early Warning System Protocol",
                "body": "The Central Water Commission (CWC) provides flood forecasting services. State governments should monitor water levels, issue timely warnings through multiple channels, and prepare for evacuations in vulnerable areas.",
                "phase": "Preparedness",
                "authority": "Central Water Commission (CWC)"
            },
            {
                "title": "Post-Flood Recovery Guidelines",
                "body": "After floodwaters recede, authorities should conduct damage assessment, provide compensation to affected families, restore infrastructure, and implement disease prevention measures to prevent waterborne illnesses.",
                "phase": "Recovery",
                "authority": "Ministry of Home Affairs"
            },
            {
                "title": "Flood Mitigation Framework",
                "body": "Long-term flood mitigation includes construction of embankments and levees, improvement of drainage systems, watershed management, and implementation of flood plain zoning regulations to prevent encroachment.",
                "phase": "Mitigation",
                "authority": "National Disaster Management Authority (NDMA)"
            }
        ],
        "Cyclone": [
            {
                "title": "National Cyclone Risk Mitigation Project",
                "body": "This project aims to reduce vulnerability of coastal communities to cyclones through early warning systems, evacuation shelters, and coastal embankments. States should ensure regular drills and awareness programs.",
                "phase": "Preparedness",
                "authority": "National Disaster Management Authority (NDMA)"
            },
            {
                "title": "Cyclone Evacuation Protocol",
                "body": "Upon cyclone warning, authorities should evacuate vulnerable coastal populations to designated cyclone shelters, deploy emergency response teams, and ensure essential supplies for at least 72 hours.",
                "phase": "Response",
                "authority": "State Disaster Management Authorities"
            },
            {
                "title": "Post-Cyclone Damage Assessment Guidelines",
                "body": "After cyclone passage, conduct immediate aerial surveys, restore communication networks, clear debris, and provide emergency medical assistance to affected populations.",
                "phase": "Recovery",
                "authority": "Ministry of Home Affairs"
            },
            {
                "title": "Cyclone Resistant Infrastructure Standards",
                "body": "All coastal structures should comply with BIS standards for wind resistance. Government buildings in cyclone-prone areas must be constructed as multi-purpose cyclone shelters.",
                "phase": "Mitigation",
                "authority": "Bureau of Indian Standards (BIS)"
            }
        ],
        "Drought": [
            {
                "title": "Manual for Drought Management",
                "body": "This comprehensive manual outlines procedures for declaration of drought, implementation of relief measures, and coordination mechanisms between central and state authorities.",
                "phase": "Response",
                "authority": "Ministry of Agriculture & Farmers Welfare"
            },
            {
                "title": "National Water Conservation Strategy",
                "body": "States should implement watershed development programs, rainwater harvesting, and promote drought-resistant crops. The Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA) should be leveraged for water conservation works.",
                "phase": "Mitigation",
                "authority": "Ministry of Jal Shakti"
            },
            {
                "title": "Drought Monitoring Framework",
                "body": "The India Meteorological Department (IMD) and state agriculture departments should monitor rainfall deficiency, reservoir levels, groundwater status, and crop conditions to provide early warnings of drought conditions.",
                "phase": "Preparedness",
                "authority": "India Meteorological Department (IMD)"
            },
            {
                "title": "Drought Relief Implementation Guidelines",
                "body": "During declared droughts, authorities should ensure drinking water supply through tankers, provide fodder for livestock, implement food security measures, and offer employment through MGNREGA.",
                "phase": "Response",
                "authority": "State Relief Commissioners"
            }
        ],
        "Earthquake": [
            {
                "title": "National Earthquake Response Protocol",
                "body": "Immediate deployment of Urban Search and Rescue Teams, establishment of Emergency Operations Centers, and activation of medical response teams. The protocol includes building damage assessment and categorization procedures.",
                "phase": "Response",
                "authority": "National Disaster Management Authority (NDMA)"
            },
            {
                "title": "Earthquake Preparedness Guidelines",
                "body": "Conducts regular mock drills, structural assessments of critical infrastructure, and public awareness campaigns on earthquake safety. Maintain emergency supplies and develop family emergency plans.",
                "phase": "Preparedness",
                "authority": "NDMA and State Disaster Management Authorities"
            },
            {
                "title": "Post-Earthquake Reconstruction Policy",
                "body": "Framework for reconstruction with earthquake-resistant designs, financial assistance schemes for affected families, and guidelines for transitional shelter arrangements.",
                "phase": "Recovery",
                "authority": "Ministry of Housing and Urban Affairs"
            },
            {
                "title": "National Building Code - Seismic Provisions",
                "body": "Mandatory implementation of seismic codes in construction, seismic microzonation of urban areas, and retrofitting of existing critical infrastructure in high-risk zones.",
                "phase": "Mitigation",
                "authority": "Bureau of Indian Standards (BIS)"
            }
        ],
        "Landslide": [
            {
                "title": "National Landslide Risk Management Strategy",
                "body": "Comprehensive approach to landslide risk assessment, early warning systems in vulnerable hill areas, and regulation of construction activities on steep slopes.",
                "phase": "Preparedness",
                "authority": "Geological Survey of India (GSI)"
            },
            {
                "title": "Landslide Response Guidelines",
                "body": "Protocols for immediate search and rescue operations, temporary relocation of affected communities, and restoration of critical infrastructure like roads and communication networks.",
                "phase": "Response",
                "authority": "National Disaster Response Force (NDRF)"
            },
            {
                "title": "Hill Area Development Program",
                "body": "Long-term strategy for sustainable development in landslide-prone regions, including afforestation, proper drainage systems, and slope stabilization measures.",
                "phase": "Mitigation",
                "authority": "Ministry of Environment, Forest and Climate Change"
            },
            {
                "title": "Guidelines for Reconstruction in Landslide Affected Areas",
                "body": "Technical specifications for rebuilding in affected areas, relocation policies for highly vulnerable settlements, and land-use planning to minimize future risks.",
                "phase": "Recovery",
                "authority": "State Disaster Management Authorities"
            }
        ],
        "Heat Wave": [
            {
                "title": "National Action Plan on Heat Related Illnesses",
                "body": "Comprehensive strategy for prevention and management of heat-related illnesses, including public cooling centers, emergency medical protocols, and vulnerable population identification.",
                "phase": "Response",
                "authority": "Ministry of Health and Family Welfare"
            },
            {
                "title": "Heat Wave Guidelines for States",
                "body": "Framework for declaring heat waves, color-coded alert system, and standard operating procedures for different departments during extreme heat events.",
                "phase": "Preparedness",
                "authority": "National Disaster Management Authority (NDMA)"
            },
            {
                "title": "Cool Roof Program",
                "body": "Implementation of cool roofs in public buildings, incentives for private adoption, and urban planning guidelines to reduce urban heat island effect.",
                "phase": "Mitigation",
                "authority": "Ministry of Housing and Urban Affairs"
            },
            {
                "title": "Heat Action Plan for Vulnerable Groups",
                "body": "Special provisions for outdoor workers, elderly, children, and pregnant women during heat waves, including work hour adjustments and targeted outreach.",
                "phase": "Response",
                "authority": "Ministry of Labour and Employment"
            }
        ],
        "Cold Wave": [
            {
                "title": "Cold Wave Management Plan",
                "body": "Guidelines for establishing warming shelters, distribution of blankets and warm clothing, and monitoring of vulnerable populations including homeless individuals.",
                "phase": "Response",
                "authority": "State Disaster Management Authorities"
            },
            {
                "title": "Winter Preparedness Advisory",
                "body": "Early warnings for cold wave conditions, public education on preventing cold-related illnesses, and preparation of emergency services for increased demand.",
                "phase": "Preparedness",
                "authority": "India Meteorological Department (IMD)"
            },
            {
                "title": "Guidelines for Schools During Cold Waves",
                "body": "Protocol for school closures, adjustment of school hours, and ensuring adequate heating in educational institutions during extreme cold conditions.",
                "phase": "Response",
                "authority": "Ministry of Education"
            },
            {
                "title": "Cold Wave Relief Fund Utilization Guidelines",
                "body": "Framework for allocation and utilization of funds for cold wave relief, including procurement of essential supplies and compensation for affected families.",
                "phase": "Recovery",
                "authority": "Ministry of Home Affairs"
            }
        ],
        "Forest Fire": [
            {
                "title": "National Action Plan on Forest Fires",
                "body": "Comprehensive strategy for prevention, detection, and suppression of forest fires, including use of satellite monitoring, rapid response teams, and community involvement.",
                "phase": "Preparedness",
                "authority": "Ministry of Environment, Forest and Climate Change"
            },
            {
                "title": "Forest Fire Crisis Management Plan",
                "body": "Standard operating procedures for various agencies during forest fire emergencies, coordination mechanisms, and resource mobilization protocols.",
                "phase": "Response",
                "authority": "Forest Survey of India (FSI)"
            },
            {
                "title": "Forest Fire Prevention Guidelines",
                "body": "Implementation of fire lines, controlled burning techniques, and community awareness programs in vulnerable forest areas before fire season.",
                "phase": "Mitigation",
                "authority": "State Forest Departments"
            },
            {
                "title": "Post-Fire Ecosystem Restoration Plan",
                "body": "Framework for assessment of ecological damage, reforestation strategies, soil conservation measures, and monitoring of recovery progress.",
                "phase": "Recovery",
                "authority": "Ministry of Environment, Forest and Climate Change"
            }
        ],
        "Urban Flooding": [
            {
                "title": "Urban Flooding Standard Operating Procedure",
                "body": "Guidelines for urban local bodies on pump deployment, drainage clearance, traffic management, and evacuation of low-lying urban areas during flooding events.",
                "phase": "Response",
                "authority": "Ministry of Housing and Urban Affairs"
            },
            {
                "title": "Urban Drainage Design Manual",
                "body": "Technical specifications for urban drainage systems, integration of blue-green infrastructure, and implementation of stormwater management practices.",
                "phase": "Mitigation",
                "authority": "Central Public Works Department (CPWD)"
            },
            {
                "title": "Guidelines for Urban Flood Early Warning Systems",
                "body": "Implementation of automated rain gauges, flood sensors, and citizen reporting systems to provide localized flood warnings in urban areas.",
                "phase": "Preparedness",
                "authority": "National Disaster Management Authority (NDMA)"
            },
            {
                "title": "Post-Urban Flooding Disease Prevention Protocol",
                "body": "Measures to prevent waterborne diseases after urban flooding, including water purification, vector control, and public health surveillance.",
                "phase": "Recovery",
                "authority": "Ministry of Health and Family Welfare"
            }
        ]
    }
    
    # If disaster type is not in our predefined list, return generic strategies
    if disaster_type not in strategies:
        return [
            {
                "title": "Generic Disaster Response Protocol",
                "body": "The National Disaster Response Force (NDRF) should be deployed for search and rescue operations. State authorities should establish relief camps and provide essential supplies to affected populations.",
                "phase": "Response",
                "authority": "National Disaster Management Authority (NDMA)",
                "type": "guideline",
                "from_api": False,
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Community-Based Disaster Management",
                "body": "Local authorities should establish Community Disaster Response Teams, conduct regular drills, and maintain emergency supply stocks at the community level.",
                "phase": "Preparedness",
                "authority": "State Disaster Management Authorities",
                "type": "guideline",
                "from_api": False,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
    
    # Format the default strategies to match API response format
    formatted_strategies = []
    for strategy in strategies.get(disaster_type, []):
        formatted_strategies.append({
            "title": strategy.get("title"),
            "body": strategy.get("body"),
            "source": strategy.get("authority"),
            "phase": strategy.get("phase"),
            "type": "guideline",
            "from_api": False,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
    
    return formatted_strategies
