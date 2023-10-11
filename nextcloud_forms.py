import requests
import json
import datetime

headers = {
    'Accept': 'application/json, text/plain, */*',
    'OCS-APIRequest': 'true',
}

class nextcloud_form:
    def __init__(self, nextcloud_url, nextcloud_user, nextcloud_password):
        if nextcloud_url.endswith('/'):
            self.base_url = nextcloud_url
        else:
            self.base_url = "{}/".format(nextcloud_url)
        self.username = nextcloud_user
        self.password = nextcloud_password

    def do_get(self,api_path):
        return_status = "Request was never sent"
        json_obj = []
        if api_path.startswith('/'):
            api_path = api_path[1:]
        response = requests.get("{}{}".format(self.base_url,api_path), auth=(self.username,self.password), headers=headers)
        if response.status_code >= 200 and response.status_code < 300:
            json_obj = response.json()
            try:
                json_obj = response.json()
                return_status = "OK"
            except JSONDecodeError as e:
                return_status = "FAIL"
        else:
            return_status = "FAIL HTTP {}".format(response.status_code)
        return {"status":return_status,"json":json_obj}

    def list_owned_forms(self):
        return self.do_get("/ocs/v2.php/apps/forms/api/v2.1/forms")

    def get_owned_forms_hash_list(self):
        form_object = self.do_get("/ocs/v2.php/apps/forms/api/v2.1/forms")
        hash_list = []
        for form in form_object["json"]["ocs"]["data"]:
            hash_list.append(form["hash"])
        return hash_list

    def get_partial_form(self, hashid):
        return self.do_get("/ocs/v2.php/apps/forms/api/v2.1/partial_form/{}".format(hashid))

    def get_form_questions(self, hashid):
        return self.do_get("/ocs/v2.php/apps/forms/api/v2.1/form/{}".format(self.get_partial_form(hashid)["json"]["ocs"]["data"]["id"]))

    def get_submissions(self, hashid):
        return self.do_get("/ocs/v2.php/apps/forms/api/v2.1/submissions/{}".format(hashid))

