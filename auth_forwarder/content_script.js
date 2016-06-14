/**
 * Content script for the Chrome extension.
 */

// Add listeners for LiveVox Redirect. Code not related to this hack
// has been removed due to restrictions on disclosure. The conditions for
// attempting the redirect are additionally linked to a domain. 
$(function() {
    var origin = window.location.origin;

    var jsession = null, token = null, uname = null;
    if (window.location.pathname.indexOf("AgentLogin") !== -1 &&
            get_param !== undefined) {
        jsession = get_param('jsessionid');
        token = get_param('token');
        uname = get_param('agentName');
    }

    if(jsession != null && token != null && uname != null) {
        Document.cookie = "JSESSIONID=" + jsession;
        window.location = 'https://lvacd.livevox.com/VirtualACD_2.8.119/agentpanel/' +
            'AgentPanel.jsp?client_id=71623&agent_id=' + uname + '&token=' + token;
    }
});
