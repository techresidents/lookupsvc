namespace java com.techresidents.services.lookupsvc.gen
namespace py trlookupsvc.gen

include "core.thrift"

enum LookupScope {
    LOCATION = 0,
    POSITION = 1,
    TAG = 2,
    TECHNOLOGY = 3,
}

struct LookupResult {
    1: i32 id,
    2: string value,
    3: map<string, string> data,
}

service TLookupService extends core.TRService
{
    list<LookupResult> lookup(
            1: core.RequestContext requestContext,
            2: LookupScope scope,
            3: string category,
            4: string value,
            ),
}
