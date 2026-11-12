const now = luxon.DateTime.now();
let upcoming_div = "";
let past_div = "";
let hidden_div = "";
let events_title_date = "";


function event_click_event(info){
    const eventElement = document.getElementById(info.event.extendedProps.eventId)
    eventElement.scrollIntoView({behavior: 'smooth'}); 
    eventElement.classList.add("animate-borderflash")
}
function update_event_data(info) {
    let reference_date = "";

    if(!info)
    {
        reference_date = now;
        events_title_date.innerHTML = "This Week"
    }
    else {
        const info_start = luxon.DateTime.fromJSDate(info.view.currentStart);
        const info_end = luxon.DateTime.fromJSDate(info.view.currentEnd);
        if (now >= info_start && now <= info_end) {
            events_title_date.innerHTML = "This Week"
            reference_date = now;
        }
        else {
            events_title_date.innerHTML = "Week of " + info_start.month + "/" + info_start.day
            reference_date = info_start;
        }
    }

    [...document.querySelectorAll(".animate-borderflash")].forEach( div => {
        div.classList.remove("animate-borderflash");
    })

    let events = [...document.querySelectorAll(".eventcard")];
    events.forEach( event_div => {
        let dateObj = luxon.DateTime.fromISO(event_div.dataset.date)
        if(event_div.dataset.state == "upcoming") {
            upcoming_div.removeChild(event_div);
        }
        else if(event_div.dataset.state == "past") {
            past_div.removeChild(event_div);
        }
        else if(event_div.dataset.state == "hidden") {
            hidden_div.removeChild(event_div);
        }

        if(dateObj.localWeekNumber == reference_date.localWeekNumber){
            if(dateObj >= reference_date){
                upcoming_div.appendChild(event_div);
                event_div.dataset.state = "upcoming";
            }
            else if(dateObj < reference_date) {
                past_div.appendChild(event_div)
                event_div.dataset.state = "past";
            }
        }
        else {
            hidden_div.appendChild(event_div);
            event_div.dataset.state = "hidden";
        }

    });

    if (upcoming_div.childElementCount == 1){
        upcoming_div.querySelector(".theresnothing").classList.remove("hidden")
    }
    else {
        upcoming_div.querySelector(".theresnothing").classList.add("hidden")
    }
    if (past_div.childElementCount == 1){
        past_div.querySelector(".theresnothing").classList.remove("hidden")
    }
    else {
        past_div.querySelector(".theresnothing").classList.add("hidden")
    }
}