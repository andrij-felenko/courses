-- Ранній прототип маршрутизації у mysql-proxy (2007)
function read_query(packet)
    if packet:byte() == proxy.COM_QUERY then
        local query = packet:sub(2)
        if query:match("^%s*[Ss][Ee][Ll][Ee][Cc][Tt]") then
            proxy.connection.backend_ndx = 2 -- Slave Backend
        else
            proxy.connection.backend_ndx = 1 -- Master Backend
        end
    end
end
