from typing import Optional, List, Dict, Any
import requests
from flask import current_app
from app.schemas.search import PacienteSearch
from app.services.translate import TranslateService

class SearchService:
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def __init__(self):
        self.translate_service = TranslateService()

    @staticmethod
    def filter_studies(api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        filtered_studies = []

        for study in api_response.get("studies", []):
            filtered_study = {}
            protocol_section = study.get("protocolSection", {})
            identification_module = protocol_section.get("identificationModule", {})
            description_module = protocol_section.get("descriptionModule", {})
            arms_interventions_module = protocol_section.get("armsInterventionsModule", {})
            sponsors_collaborators_module = protocol_section.get("sponsorsCollaboratorsModule", {})
            contacts_locations_module = protocol_section.get("contactsLocationsModule", {})
            conditions_module = protocol_section.get("conditionsModule", {})
            eligibility_module = protocol_section.get("eligibilityModule", {})

            title = identification_module.get("briefTitle") or identification_module.get("officialTitle") or "N/A"
            filtered_study["Title"] = title

            brief_summary = description_module.get("briefSummary", "")
            detailed_description = description_module.get("detailedDescription", "")
            full_description = "\n\n".join(filter(None, [brief_summary, detailed_description])).strip() or "N/A"
            filtered_study["Description"] = full_description

            interventions = arms_interventions_module.get("interventions", [])
            intervention_names = [interv.get("name", "N/A") for interv in interventions] or ["N/A"]
            filtered_study["Intervention"] = intervention_names

            sponsor = sponsors_collaborators_module.get("leadSponsor", {}).get("name", "N/A")
            filtered_study["Sponsor"] = sponsor

            keywords = conditions_module.get("keywords", []) or ["N/A"]
            filtered_study["Keywords"] = keywords

            contacts = contacts_locations_module.get("centralContacts", []) or ["N/A"]
            filtered_study["Contacts"] = contacts

            locations = contacts_locations_module.get("locations", [])
            location_info = []
            for loc in locations:
                facility = loc.get("facility", "N/A")
                city = loc.get("city", "N/A")
                state = loc.get("state", "N/A")
                country = loc.get("country", "N/A")
                status = loc.get("status", "N/A")
                location_info.append({
                    "Facility": facility,
                    "City": city,
                    "State": state,
                    "Country": country,
                    "Status": status
                })
            filtered_study["Location"] = location_info or ["N/A"]

            conditions = conditions_module.get("conditions", []) or ["N/A"]
            filtered_study["Conditions"] = conditions

            restrictions = eligibility_module.get("eligibilityCriteria", "N/A").strip()
            filtered_study["Restrictions"] = restrictions

            has_results = study.get("hasResults", False)
            filtered_study["Has Results Published"] = has_results

            filtered_studies.append(filtered_study)

        return filtered_studies

    def search_paciente(
        self,
        search_data: PacienteSearch,
        fields: Optional[List[str]] = None,
        page_size: int = 3,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        search_url = self.BASE_URL
        params = {
            "format": "json",
            "pageSize": page_size
        }

        data_dict = search_data.dict(exclude_none=True, exclude_unset=True, by_alias=True)
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

        if fields:
            params['fields'] = ",".join(fields)

        current_app.logger.info(f"Initial Params: {params}")

        next_page_token = None
        current_page = 1
        while current_page <= page:
            if next_page_token:
                params['pageToken'] = next_page_token

            response = requests.get(search_url, params=params)
            if response.status_code != 200:
                self.handle_api_error(response)

            api_response = response.json()

            if current_page == page:
                filtered_response = self.filter_studies(api_response)

                if search_data.location:
                    filtered_response = self.filter_by_location(filtered_response, search_data.location)
                    # places can have different statuses compared to the overall, so i filter them here
                    for study in filtered_response:
                        if study["Location"][0]["Status"] == search_data.status:
                            continue 
                        else:
                            filtered_response.remove(study)

                self.translate_service.translate_fields(filtered_response)

                return filtered_response

            next_page_token = api_response.get('nextPageToken')
            if not next_page_token:
                break

            current_page += 1

        return []

    def filter_by_location(self, studies: List[Dict[str, Any]], location: str) -> List[Dict[str, Any]]:
        filter_city = location.split(",")[0].strip().lower()
        filtered_studies = []

        for study in studies:
            for loc in study["Location"]:
                if isinstance(loc, dict) and filter_city in loc.get("City", "").lower():
                    study["Location"] = [loc] 
                    filtered_studies.append(study)
                    break

        return filtered_studies

    @staticmethod
    def handle_api_error(response: requests.Response):
        try:
            error_details = response.json()
        except ValueError:
            error_details = response.text
        raise requests.exceptions.HTTPError(
            f"{response.status_code} Client Error: {response.reason} for url: {response.url}\nDetails: {error_details}",
            response=response
        )
