const now = luxon.DateTime.now();
var upcomingDiv = "";
var pastDiv = "";
var hiddenDiv = "";
var eventsTitleDate = "";

function eventClickEvent(info){
    const eventElement = document.getElementById(info.event.extendedProps.eventId)
    if (!eventElement) {
        return;
    }

    eventElement.scrollIntoView({behavior: 'smooth'}); 
    eventElement.classList.add("animate-borderflash");
    setTimeout(() => {eventElement.classList.remove("animate-borderflash")}, 2000);
}

function updateEventData(info) {
    let referenceDate = "";

    if(!info)
    {
        referenceDate = now;
        eventsTitleDate.innerHTML = "This Week"
    }
    else {
        const infoStart = luxon.DateTime.fromJSDate(info.view.currentStart);
        const infoEnd = luxon.DateTime.fromJSDate(info.view.currentEnd);
        if (now >= infoStart && now <= infoEnd) {
            eventsTitleDate.innerHTML = "This Week"
            referenceDate = now;
        }
        else {
            eventsTitleDate.innerHTML = `Week of ${infoStart.month}/${infoStart.day}`;
            referenceDate = infoStart;
        }
    }

    document.querySelectorAll(".eventcard").forEach( eventDiv => {
        let dateObj = luxon.DateTime.fromISO(eventDiv.dataset.date)
        if(eventDiv.dataset.state === "upcoming") {
            upcomingDiv.removeChild(eventDiv);
        }
        else if(eventDiv.dataset.state === "past") {
            pastDiv.removeChild(eventDiv);
        }
        else if(eventDiv.dataset.state === "hidden") {
            hiddenDiv.removeChild(eventDiv);
        }

        if(dateObj.localWeekNumber === referenceDate.localWeekNumber){
            if(dateObj >= referenceDate){
                upcomingDiv.appendChild(eventDiv);
                eventDiv.dataset.state = "upcoming";
            }
            else if(dateObj < referenceDate) {
                pastDiv.appendChild(eventDiv)
                eventDiv.dataset.state = "past";
            }
        }
        else {
            hiddenDiv.appendChild(eventDiv);
            eventDiv.dataset.state = "hidden";
        }

    });

    if (upcomingDiv.childElementCount === 1){
        upcomingDiv.querySelector(".theresnothing").classList.remove("hidden")
    }
    else {
        upcomingDiv.querySelector(".theresnothing").classList.add("hidden")
    }

    if (pastDiv.childElementCount === 1){
        pastDiv.querySelector(".theresnothing").classList.remove("hidden")
    }
    else {
        pastDiv.querySelector(".theresnothing").classList.add("hidden")
    }
}