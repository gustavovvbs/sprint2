from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import requests
from flask import current_app
from app.schemas.search import PacienteSearch

class SearchService:
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def __init__(self):
        pass

    @staticmethod
    def filter_studies(api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        filtered_studies = []
        
        for study in api_response.get("studies", []):
            filtered_study = {}
            
            identification = study.get("protocolSection", {}).get("identificationModule", {})
            title = identification.get("briefTitle") or identification.get("officialTitle") or "N/A"
            filtered_study["Title"] = title

            description = study.get("protocolSection", {}).get("descriptionModule", {})
            brief_summary = description.get("briefSummary", "")
            detailed_description = description.get("detailedDescription", "")
            if brief_summary and detailed_description:
                full_description = f"{brief_summary}\n\n{detailed_description}"
            elif brief_summary:
                full_description = brief_summary
            elif detailed_description:
                full_description = detailed_description
            else:
                full_description = "N/A"
            filtered_study["Description"] = full_description.strip()
            
            interventions_module = study.get("protocolSection", {}).get("armsInterventionsModule", {})
            interventions = interventions_module.get("interventions", [])
            intervention_names = [interv.get("name", "N/A") for interv in interventions]
            filtered_study["Intervention"] = intervention_names if intervention_names else ["N/A"]
            
            officials = study.get("protocolSection", {}).get("contactsLocationsModule", {}).get("overallOfficials", [])
            people_involved = [official.get("name", "N/A") for official in officials]
            filtered_study["People Involved"] = people_involved if people_involved else ["N/A"]
            
            locations = study.get("protocolSection", {}).get("contactsLocationsModule", {}).get("locations", [])
            location_info = []
            for loc in locations:
                facility = loc.get("facility", "N/A")
                city = loc.get("city", "N/A")
                state = loc.get("state", "N/A")
                country = loc.get("country", "N/A")
                location_str = f"{facility}, {city}, {state}, {country}"
                location_info.append({
                    "Facility": facility,
                    "City": city,
                    "State": state,
                    "Country": country,
                    "status": loc.get("status", "N/A")
                })


            filtered_study["Location"] = location_info if location_info else ["N/A"]
            
            conditions_module = study.get("protocolSection", {}).get("conditionsModule", {})
            conditions = conditions_module.get("conditions", [])
            filtered_study["Conditions"] = conditions if conditions else ["N/A"]
            
            eligibility_module = study.get("protocolSection", {}).get("eligibilityModule", {})
            study_type = eligibility_module.get("studyType", "N/A")
            study_phase = eligibility_module.get("phase", "N/A")
            min_age = eligibility_module.get("minimumAge", "N/A")
            # filtered_study["Age"] = age
            
            restrictions = eligibility_module.get("eligibilityCriteria", "N/A")
            filtered_study["Restrictions"] = restrictions.strip()
            
            # Se tem resultados publicados
            has_results = study.get("hasResults", False)
            filtered_study["Has Results Published"] = has_results
            
            filtered_studies.append(filtered_study)
        
        return filtered_studies

    @staticmethod
    def search_paciente(search_data: PacienteSearch, fields: Optional[List[str]] = None, page_size: int = 10) -> List[Dict[str, Any]]:
        search_url = SearchService.BASE_URL

        params = {
            "format": "json",
            "pageSize": page_size
        }

        data_dict = search_data.dict(
            exclude_none=True,
            exclude_unset=True,
            by_alias=True
        )
        current_app.logger.info(f"Search data: {data_dict}")
        if 'age' in data_dict and data_dict['age']:
            age_value = data_dict.pop('age')
            age_expr = f"AREA[MinimumAge]RANGE[MIN, {age_value}] AND AREA[MaximumAge]RANGE[{age_value}, MAX]"
            params['filter.advanced'] = age_expr

        for key, value in data_dict.items():
            if isinstance(value, list):
                params[key] = ",".join(value)
            else:
                params[key] = value

        if fields is not None:
            params['fields'] = ",".join(fields)

        current_app.logger.info(f"Final Params: {params}")

        response = requests.get(search_url, params=params)

        if response.status_code == 200:
            api_response = response.json()
            filtered_response = SearchService.filter_studies(api_response)
            filter_city = search_data.location.split(",")[0]
            filtered_per_location = []
            for study in filtered_response:
                for location in study["Location"]:
                    if filter_city.lower() in location["City"].lower():
                        study["Location"] = location
                        filtered_per_location.append(study)
                        break

            return filtered_per_location
        else:
            try:
                error_details = response.json()
            except ValueError:
                error_details = response.text
            raise requests.exceptions.HTTPError(
                f"{response.status_code} Client Error: {response.reason} for url: {response.url}\nDetails: {error_details}",
                response=response
            )
