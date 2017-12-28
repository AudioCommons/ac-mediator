from services.acservice.constants import LICENSE_UNKNOWN, LICENSE_CC0, LICENSE_CC_BY, LICENSE_CC_BY_NC, \
    LICENSE_CC_BY_NC_ND, LICENSE_CC_BY_NC_SA, LICENSE_CC_BY_ND, LICENSE_CC_BY_SA, LICENSE_CC_SAMPLING_PLUS
from pyparsing import CaselessLiteral, Word, alphanums, alphas8bit, nums, quotedString, \
    operatorPrecedence, opAssoc, removeQuotes, Literal, Group, Suppress, Combine


def translate_cc_license_url(url):
    """
    Return CC license name from license URL
    """
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


# Util functions for parsing filters, define grammar and parsing functions
# Parsing is done using Pyparsing library. Relevant documentation for Pyparsing can be found here:
# http://shop.oreilly.com/product/9780596514235.do

def as_number_if_number(x):
    try:
        x = float(x[0])  # Cast to float
        if x.is_integer():
            x = int(x)  # If is whole number, cast to integer
    except ValueError as e:
        pass
    return x  # If casting fails, return as is


alphanums_plus = alphanums + '_'  # Allow underscore character in filter name
float_nums = nums + '.'  # Allow float numbers
and_ = CaselessLiteral("and")
or_ = CaselessLiteral("or")
not_ = CaselessLiteral("not")
filterValueText = (Word(alphanums_plus + alphas8bit + float_nums + '-') | quotedString.setParseAction(removeQuotes))\
    .setParseAction(as_number_if_number)
number_or_asterisk = (Literal('*') | Word(float_nums)).setParseAction(as_number_if_number)
filterValueRange = Group(Suppress(Literal('[')).suppress() + number_or_asterisk + Suppress(Literal(',')).suppress() +
                         number_or_asterisk + Suppress(Literal(']')).suppress())
fieldName = Combine(Word(alphanums) + Literal(':') + Word(alphanums_plus))  # ontologyPrefix:givenFieldName
filterTerm = Group(fieldName + Literal(':') + (filterValueText | filterValueRange))  # ontologyPrefix:givenFieldName:filterValue
filterExpr = operatorPrecedence(filterTerm,
                                [
                                    (not_, 1, opAssoc.RIGHT),
                                    (and_, 2, opAssoc.LEFT),
                                    (or_, 2, opAssoc.LEFT),
                                ])


def parse_filter(filter_string):
    """
    Parse a filter string using the 'filterExpr' grammar defined above.
    This function returns a pyparsing.ParseResults object that should be further
    processed with the build_filter_string method of a ACServiceTextSearchMixin instance.
    """
    return filterExpr.parseString(filter_string, parseAll=True)
