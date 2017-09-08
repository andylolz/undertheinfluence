function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

var companyId = getParameterByName('companyid');
var company = getParameterByName('company');
if(company) {
    document.getElementById("form").action = "http://www.appc.org.uk/register/profile/?company=" + company;
    document.getElementById("submit").innerText = "Redirect to " + company + " (APPC register)";
    document.getElementById("companyid").value = companyId;
}
