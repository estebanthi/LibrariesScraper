import yaml

import src.mam as mam


if __name__ == "__main__":
    config = yaml.safe_load(open("config.yml"))
    cookie = config["cookie"]
    user_agent = config["user_agent"]

    start = 0
    end = 100

    requests = mam.get_requests(start, end, cookie, user_agent)
    requests = mam.filter_requests(requests, lang_codes=None)
    mam.save_requests(requests, "out/requests.json")
