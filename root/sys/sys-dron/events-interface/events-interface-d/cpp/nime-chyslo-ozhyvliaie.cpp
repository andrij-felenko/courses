void EventHandler::Impl::gotEvent(const mavlink_event_t &event)
{
    if (!parser.hasDefinitions()) {
        if (pendingEvents.size() > 50) {   // стеля, до якої в нормі не доходить
            pendingEvents.clear();
        }
        pendingEvents.push_back(event);
        return;
    }

    std::unique_ptr<events::parser::ParsedEvent> parsed_event =
        parser.parse(events::EventType(event));
    if (parsed_event == nullptr) {
        qCWarning(EventHandlerLog) << "Got Event w/o known metadata: ID:" << event.id;
        return;
    }
    ...
}
