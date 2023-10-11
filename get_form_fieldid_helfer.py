import nextcloud_forms
import json
import sys
import yaml


exec(open("{}/config.py".format(sys.path[0])).read())

global_params["form_id"] = sys.argv[1]

form = nextcloud_forms.nextcloud_form(nextcloud_url=global_params["nextcloud_url"], nextcloud_user=global_params["nextcloud_user"], nextcloud_password=global_params["nextcloud_password"])
if global_params["form_id"] not in form.get_owned_forms_hash_list():
    print("Could not find Form with hash: {}".format(global_params["form_id"]))
    exit()
else:
    questions_object = form.get_form_questions(global_params["form_id"])["json"]["ocs"]["data"]["questions"]
    pretty_dict = []
    for question_object in questions_object:
        pretty_dict.append({"ID":question_object["id"], "Text":question_object["text"]})
    print(yaml.dump(pretty_dict, default_flow_style=False))
