def group_by_company_name(company_data, info):
    company_name = info["company"]
    if company_name not in company_data:
        company_data[company_name] = []
    company_data[company_name].append(info)
