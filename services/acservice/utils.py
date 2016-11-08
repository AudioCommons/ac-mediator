from services.acservice.constants import LICENSE_UNKNOWN, LICENSE_CC0, LICENSE_CC_BY, LICENSE_CC_BY_NC, \
    LICENSE_CC_BY_NC_ND, LICENSE_CC_BY_NC_SA, LICENSE_CC_BY_ND, LICENSE_CC_BY_SA, LICENSE_CC_SAMPLING_PLUS


def translate_cc_license_url(url):
    # TODO: this does not include license versioning (3.0, 4.0...)
    if '/by/' in url: return LICENSE_CC_BY
    if '/by-nc/' in url: return LICENSE_CC_BY_NC
    if '/by-nd/' in url: return LICENSE_CC_BY_ND
    if '/by-sa/' in url: return LICENSE_CC_BY_SA
    if '/by-nc-sa/' in url: return LICENSE_CC_BY_NC_SA
    if '/by-nc-nd/' in url: return LICENSE_CC_BY_NC_ND
    if '/zero/' in url: return LICENSE_CC0
    if '/publicdomain/' in url: return LICENSE_CC0
    if '/sampling+/' in url: return LICENSE_CC_SAMPLING_PLUS
    return LICENSE_UNKNOWN
