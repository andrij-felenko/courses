// Перший в історії синтаксис фонового запиту (IE 5.0, 1999)
var xhr = new ActiveXObject("MSXML2.XMLHTTP.3.0");
xhr.open("GET", "/api/inbox", true);
xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        var xmlDoc = xhr.responseXML;
        updateEmailList(xmlDoc);
    }
};
xhr.send(null);
