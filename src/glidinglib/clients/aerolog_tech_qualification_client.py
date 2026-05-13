from glidinglib.mappers.aerolog_tech_qualification_mapper import (
    map_aerolog_tech_qualification,
)

class AerologTechQualClient:
    def __init__(
        self,
        base_url,
        session,
        auth_token,
    ):
        self.base_url = base_url
        self.session = session
        self.auth_token = auth_token
        
    def get_members_tech_qualif(
        self,
        start_account: int | str,
        end_account: int | str | None = None,
    ):
        if end_account is None:
            end_account = start_account

        url = f"{self.base_url}/api/Services/GetMembersTechQualif"

        params = {
            "StartAccount": start_account,
            "EndAccount": end_account,
        }

        response = self.session.get(
            url,
            params=params,
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.auth_token}",
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        result = []

        def extract_quals(value):
            if isinstance(value, dict):

                # Found a member record containing qualifications
                if "technicalQualifications" in value:
                    account = (
                        value.get("account")
                        or value.get("accountNo")
                        or value.get("membership")
                    )

                    name = (
                        value.get("name")
                        or value.get("fullName")
                        or ""
                    )

                    for qual in value["technicalQualifications"]:
                        qual = dict(qual)
                        qual["_account"] = account
                        qual["_name"] = name
                        result.append(qual)

                # Recurse through dict values
                for v in value.values():
                    extract_quals(v)

            elif isinstance(value, list):
                for item in value:
                    extract_quals(item)

        extract_quals(data)

        return [
            map_aerolog_tech_qualification(row)
            for row in result
        ]