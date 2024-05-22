from urllib.parse import urlparse

def get_directory_name_from_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace("www.", "")
    domain_without_tld = domain.rsplit('.', 1)[0] if '.' in domain else domain
    directory_name = domain_without_tld.replace(".", "_")
    return directory_name