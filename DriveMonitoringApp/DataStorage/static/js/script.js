/**
 * Sctipr for the Drive Monitoriing Website
 * @author Antonio Jose Peñuela Lopez
 * 
 */

const body = document.querySelector("body")
const title = document.querySelector("title")
const currentUrl = window.location.href
let contenSection = null
let divSummary = null
let divContent = null
let divLogs = null
let sumSection = null
let summaryLabel = null
let logsLabel = null
let divButtons = null
let data = null;
let filters = null;
let summaryData = null
let selectedFilters = {}
let generalData = {}
let sectionBody = null
let filtersCard = null
let filtersSection = null
let sectionTitle = null
let buttonHotPlot = null
let graphicContents = null
let plotSection = null
let input = null
const logsData = []
const summaryParsedData = []
let modal = null
let URLPath =  currentUrl.replace(/(driveMonitoring)?(loadPins)?\/?\??(date=)?(\d{4})?-?(\d{2})?-?(\d{2})?$/, "")
let ULRParts = currentUrl.split("/")
if(ULRParts.length == 5 && ULRParts[ULRParts.length-1] == ""){
    history.pushState({mode: "URLUpdate"}, "", ULRParts[ULRParts.length-2])
}
/**
 * Function that shows the Loader modal and blocks the scroll on the website
 */
const runLoader = ()=>{
    if (modal == null){
        modal = document.createElement("div")
        modal.classList.add("modal", "w-full", "h-full", "bg-black/25", "top-0", "left-0", "flex", "justify-center", "items-center")
        let loaderSpace = document.createElement("div")
        loaderSpace.classList.add("w-full", "h-full", "relative", "flex", "justify-center", "items-center")
        let loaderImage = document.createElement("img")
        loaderImage.setAttribute("src", URLPath+"static/img/CTAO-Loader.png")
        loaderImage.classList.add("absolute", "translate-y-[0]", "-translate-x-[0]", "w-[22.5rem]", "h-[15rem]")
        let loaderBar = document.createElement("div")
        loaderBar.classList.add("Bar", "rounded-full", "border-[#00E4D8]", "border","absolute" , "w-[17.5rem]", "h-[17.5rem]")
        loaderSpace.appendChild(loaderBar)
        loaderSpace.appendChild(loaderImage)
        modal.appendChild(loaderSpace)
        body.appendChild(modal)
    }else{
        if(modal.classList.contains("hidden")){
            modal.classList.remove("hidden")
        }
    }
    body.classList.add("overflow-hidden")
}
/**
 * Function that locates the modal in case the modal variable is null and hides it. It also makes the website scrollable again
 */
const deactivateLoader =()=>{
    if(modal == null){
        modal = document.querySelector("div.modal")
    }
    modal.classList.add("hidden")
    body.classList.remove("overflow-hidden")
}
/**
 * Function that generates the basic structure of the website
*/
const generateStructure = ()=>{
    contenSection = document.querySelector("div.textData")
    contenSection.innerHTML = ""
    contenSection.classList.add("gap-y-3")
    sumSection = document.createElement("div")
    sumSection.classList.add("w-[66%]", "self-center")
    divSummary = document.createElement("div")
    divSummary.classList.add("w-[50%]", "bg-[#325D88]", "flex", "justify-center", "items-center", "cursor-pointer", "rounded-tl-lg", "transition", "duration-300", "ease-in-out")
    summaryLabel = document.createElement("p")
    summaryLabel.classList.add("text-white", "text-xl", "p-2", "pointer-events-none", "select-none")
    summaryLabel.appendChild(document.createTextNode("Summary"))
    divSummary.appendChild(summaryLabel)
    divLogs = document.createElement("div")
    divLogs.classList.add("w-[50%]", "bg-[#6585a6]", "flex", "justify-center", "items-center", "cursor-pointer", "rounded-tr-lg", "transition", "duration-300", "ease-in-out")
    logsLabel = document.createElement("p")
    logsLabel.classList.add("text-white", "text-xl", "p-2", "pointer-events-none", "select-none", "transition", "duration-300", "ease-in-out")
    logsLabel.appendChild(document.createTextNode("Logs"))
    divLogs.appendChild(logsLabel)
    divButtons = document.createElement("div")
    divButtons.classList.add("flex", "w-full", "rounded-t-xl")
    divButtons.appendChild(divSummary)
    divButtons.appendChild(divLogs)
    divContent = document.createElement("div")
    divContent.classList.add("flex", "flex-col", "w-full", "border", "border-x-[0.25rem]", "border-b-[0.25rem]", "border-[#325D88]", "overflow-y-scroll", "transition", "duration-300", "ease-in-out", "h-[20rem]", "py-1", "rounded-b-lg")
    sumSection.appendChild(divButtons)
    sumSection.appendChild(divContent)
    contenSection.appendChild(sumSection)
    divSummary.addEventListener("click", showSummary)
    divLogs.addEventListener("click", showLog)
}
/**
 * Function to fetch the data from mongodb, it identifies whether the web is on driveMonitoring or loadPin websites. This is the main function in the code. After fetching it generates all the buttons and structures needed for the inteaction
*/
const fetchLatestData = async(date = null) => {
    runLoader()
    let serverRes = null
    let urlParts = currentUrl.split("/")
    if(urlParts[urlParts.length-2] == "driveMonitoring" || urlParts[urlParts.length-1] == "driveMonitoring"){
        summaryParsedData.splice(0, summaryParsedData.length)
        logsData.splice(0, logsData.length)
        if(date != null){
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLogs", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({"date": date})})
            .then(response => response.json())
            generalData = await fetch("http://127.0.0.1:8000/storage/getData", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({"date": date})})
            .then(response => response.json())
        }else{
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLogs")
            .then(response => response.json())
            generalData = await fetch("http://127.0.0.1:8000/storage/getData")
            .then(response => response.json())
        }
        if(generalData.data.Message == null){
            initializeFiltersSection()
            generateStructure()
            showAllData(generalData.data)
            data = serverRes.data
            filters = serverRes.filters
            summaryData = data.filter(element => element.LogStatus != null)
            startInputButtons()
            createTopButton()
            startSummary()
            loadFilters()
            fillLogs()
        }else{
            startInputButtons()
            contenSection = document.querySelector("div.textData")
            contenSection.innerHTML = ""
            filtersSection = document.querySelector("div.filters")
            filtersSection.innerHTML = ""
            filtersSection.classList = ["filters"]
            filtersSection.classList.add("w-[25vw]", "justify-self-center", "flex", "flex-col", "gap-y-0")
            let divAlert = document.createElement("div")
            divAlert.classList.add("border-red-600", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", "p-3", "text-center", "absolute", "top-[8rem]", "left-[44%]")
            let textAlert = document.createElement("h2")
            textAlert.classList.add("text-xl", "text-red-600")
            textAlert.appendChild(document.createTextNode(generalData.data.Message))
            divAlert.appendChild(textAlert)
            contenSection.appendChild(divAlert)
        }
    }else{
        if(date != null){
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLoadPins", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({"date": date})})
            .then(response => response.json())
        }else{
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLoadPins")
            .then(response => response.json())
        }
        console.log(serverRes)
        if(serverRes.Message == null){
            startInputButtons()
            createTopButton()
            startPlotSections()
            showLoadPins(serverRes.plots)
        }else{
            startInputButtons()
            plotsArea = document.querySelector("div.plotsArea")
            plotsArea.innerHTML = ""
            let divAlert = document.createElement("div")
            divAlert.classList.add("border-red-600", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", "p-3", "text-center", "absolute", "top-[8rem]", "left-[44%]")
            let textAlert = document.createElement("h2")
            textAlert.classList.add("text-xl", "text-red-600")
            textAlert.appendChild(document.createTextNode(serverRes.Message))
            divAlert.appendChild(textAlert)
            plotsArea.appendChild(divAlert)
        }
    }
}
//input variable assignment
let isPickerOpen = false
input = document.querySelector(".input")
let description = document.querySelector(".description")
input.addEventListener("mouseover", ()=>{
    if(description.classList.contains("hidden") && !isPickerOpen){
        description.classList.remove("hidden")
    }
})
input.addEventListener("click", ()=>{
    if(!description.classList.contains("hidden")){
        description.classList.add("hidden")
    }
    input.showPicker()
    isPickerOpen = true
})
input.addEventListener("mouseout", ()=>{
    if(!description.classList.contains("hidden")){
        description.classList.add("hidden")
    }
})
window.addEventListener("click", (e)=>{
    if(isPickerOpen && e.target != input){
        isPickerOpen = false
    }
})

fetchLatestData(input.value)
/**
 * Function that fills the logsData array with the commands found on data
 */
const fillLogs = ()=>{
    if(data != null){
        data.forEach(element => {
            if(element.Command == "Park_Out" && element.Status == "command sent" || element.Command == "Park_In" && element.Status == "command sent" || element.Command == "GoToPosition" || element.Command == "Start Tracking"){
                logsData.push("-----------------------")
            }
            if(element.Status != null){
                logsData.push(element.Time+" "+element.Command+" "+element.Status)
            }else{
                logsData.push(element.Time+" "+element.Command)
            }
        });
    }
}
/**
 * Function that shows the logs when the Summary is being displayed
 * @param {*} e Its the event use to identify the button being clicked
 */
const showLog = (e)=>{
    divContent.scrollTop = 0
    if(logsData.length == 0){
        fillLogs()
    }
    if(e.target.previousSibling.classList.contains("bg-[#325D88]")){
        e.target.previousSibling.classList.remove("bg-[#325D88]")
        e.target.previousSibling.children[0].classList.remove("font-semibold")
        e.target.previousSibling.classList.add("bg-[#6585a6]")
        divLogs.classList.toggle("bg-[#6585a6]")
        divLogs.classList.toggle("bg-[#325D88]")
        logsLabel.classList.add("font-semibold")
        if(Object.keys(selectedFilters).length == 0){
            printAllLogs()
        }else{
            filterLogs()
        }
    }else{
        if(Object.keys(selectedFilters).length > 0){
            filterLogs()
        }else{
            printAllLogs()
        }
    }
}
/**
 * Function that prints all the logsData content
 */
const printAllLogs = ()=>{
    divContent.innerHTML = ""
    logsData.forEach(element => {
        if(element != "-----------------------"){
            let parragraph = document.createElement("p")
            parragraph.appendChild(document.createTextNode(element))
            parragraph.classList.add("text-lg", "ms-2")
            divContent.appendChild(parragraph)
        }else{
            let separator = document.createElement("hr")
            separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
            divContent.appendChild(separator)
        }
    })
}
/**
 * Function that filters the logs to the selected time, date and operation and shows only that section
 */
const filterLogs = ()=>{
    divContent.innerHTML = ""
    let prevLine = null
    let dataFound = null
    let increment = 0
    if(selectedFilters["time"] != "All"){
        while(dataFound == null){
            let element = logsData[increment].split(" ")
            if (element[0] != "-----------------------"){
                if(selectedFilters["operation"] == "All"){
                    if(element[0].includes(selectedFilters["time"])){
                        dataFound = increment
                    }
                }else{
                    if(element[0] == selectedFilters["time"]){
                        dataFound = increment
                    }else if(element[0][0] == selectedFilters["time"][0] && element[0][1] == selectedFilters["time"][1] && element[0][2] == selectedFilters["time"][2] && element[0][3] == selectedFilters["time"][3] && element[0][4] == selectedFilters["time"][4] && element[0][5] == selectedFilters["time"][5] && element[0][6] == selectedFilters["time"][6]){
                        dataFound = increment
                    }
                }
            }else{
                prevLine = increment
            }
            increment++
        }
        for (let i = prevLine; i < prevLine+100; i++) {
            if(i == logsData.length){
                let separator = document.createElement("hr")
                separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
                divContent.appendChild(separator)
                break
            }
            if(logsData[i] == "-----------------------"){
                let separator = document.createElement("hr")
                separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
                divContent.appendChild(separator)
                if(i != prevLine){
                    lastLine = i
                    break
                }
            }else{
                if(i == dataFound){
                    let parragraph = document.createElement("p")
                    parragraph.appendChild(document.createTextNode(logsData[i]))
                    parragraph.classList.add("text-lg", "ms-2", "text-[#325D88]", "font-semibold")
                    divContent.appendChild(parragraph)
                }else{
                    let parragraph = document.createElement("p")
                    parragraph.appendChild(document.createTextNode(logsData[i]))
                    parragraph.classList.add("text-lg", "ms-2")
                    divContent.appendChild(parragraph)
                }
            }
        }
    }else if(selectedFilters["operation"] != "All"){
        selectedOption = null
        switch(true){
            case selectedFilters["operation"] == "GoToPos":
                selectedOption = "GoToPosition"
                break
            case selectedFilters["operation"] == "Park-in":
                selectedOption = "Park_In command sent"
                break
            case selectedFilters["operation"] == "Park-out":
                selectedOption = "Park_Out command sent"
                break
            case selectedFilters["operation"] == "Track":
                selectedOption = "Start Tracking"
                break
        }
        let prevLine = null
        logsData.forEach((line, i, array) => {
            if(line.includes(selectedOption) && prevLine == null){
                let separator = document.createElement("hr")
                separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
                divContent.appendChild(separator)
                let parragraph = document.createElement("p")
                parragraph.appendChild(document.createTextNode(line))
                parragraph.classList.add("text-lg", "ms-2")
                divContent.appendChild(parragraph)
                prevLine = i-1
            }else if(line == array[0] && prevLine != null){
                prevLine = null
            }else if(prevLine != null){
                let parragraph = document.createElement("p")
                parragraph.appendChild(document.createTextNode(line))
                parragraph.classList.add("text-lg", "ms-2")
                divContent.appendChild(parragraph)
            }
        })
        let separator = document.createElement("hr")
        separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
        divContent.appendChild(separator)
    }else{
        printAllLogs()
    }
}
/**
 * Function that fills the summaryParsedData array with the commands found on summaryData
 */
const fillSummary = ()=>{
    if(summaryData != null){
        summaryData.forEach(element =>{
            if(element.LogStatus == "Stopped"){
                summaryParsedData.push(element.Time+" -> "+element.Command+" was "+element.LogStatus.toLowerCase()+" by user")
            }else if(element.LogStatus == "Error"){
                summaryParsedData.push(element.Time+" -> "+element.Command+" had an "+element.LogStatus.toLowerCase())
            }else if(element.LogStatus == "Unknown"){
                summaryParsedData.push(element.Time+" -> "+element.LogStatus+" status")

            }else{
                summaryParsedData.push(element.Time+" -> "+element.Command+" was "+element.LogStatus.toLowerCase())
            }
        })
    }
}
/**
 * Function that shows the summary again once Logs where being showed
 * @param {*} e Its the event use to identify the button being clicked
 */
const showSummary = (e)=>{
    divContent.scrollTop = 0
    if(e.target.nextSibling.classList.contains("bg-[#325D88]")){
        divContent.classList.remove("overflow-y-scroll")
        setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
        e.target.nextSibling.classList.remove("bg-[#325D88]")
        e.target.nextSibling.children[0].classList.remove("font-semibold")
        e.target.nextSibling.classList.add("bg-[#6585a6]")
        divSummary.classList.toggle("bg-[#6585a6]")
        divSummary.classList.toggle("bg-[#325D88]")
        summaryLabel.classList.add("font-semibold")
        divContent.innerHTML = ""
        startSummary()
    }
}
/**
 * Function that fills the summary in case it is empty and represents all the commands on the summaryParsedData inside the summary are on the DriveMonitoring Web
 */
const startSummary = ()=>{
    if(summaryParsedData.length == 0){
        fillSummary()
    }
    summaryParsedData.forEach(element => {
        let parragraph = document.createElement("p")
        parragraph.appendChild(document.createTextNode(element))
        if(element.includes("error")){
            parragraph.classList.add("text-red-500")
        }else if(element.includes("status")){
            parragraph.classList.add("text-yellow-500")
        }else if(!element.includes("by user")){
            parragraph.classList.add("text-black")
        }else{
            parragraph.classList.add("font-semibold")
        }
        parragraph.classList.add("text-lg", "ms-2")
        divContent.appendChild(parragraph)
    })
}
/**
 * Initialization of the Filters section, just the space
 */
const initializeFiltersSection = ()=>{
    filtersSection = document.querySelector("div.filters")
    if(filtersSection == null){
        filtersSection = document.createElement("div")
    }
    filtersSection.innerHTML = ""
    filtersSection.classList.add("w-[25vw]", "fixed", "left-[2rem]", "top-[7.75rem]", "border-r-[#3e3f3a]", "border-r-[0.15rem]", "border-opacity-50", "h-[15rem]", "flex", "flex-col", "items_center")
    filtersCard = document.createElement("div")
    filtersCard.classList.add("w-[95%]", "mt-5")
    filtersSection.appendChild(filtersCard)
    sectionTitle = document.createElement("h3")
    sectionTitle.classList.add("text-lg", "self-center", "text-white", "w-full", "bg-[#325D88]", "rounded-t-lg", "text-center", "py-1")
    sectionTitle.appendChild(document.createTextNode("Filters"))
    sectionBody = document.createElement("div")
    sectionBody.classList.add("border", "border-[#325D88]", "border-[0.25rem]", "border-t-0", "w-full", "h-[10rem]", "rounded-b-lg", "flex", "flex-col", "items-center")
    buttonHotPlot = document.createElement("div")
    buttonHotPlot.classList.add("hotPlots", "rounded-xl", "bg-[#00004A]", "text-white", "flex", "items-center", "justify-center", "mt-5", "w-[12.5rem]", "p-2", "hover:cursor-pointer", "self-center", "text-xl", "border-[#00E4D8]", "border")
    buttonHotPlot.appendChild(document.createTextNode("Create latest plots"))
    buttonHotPlot.addEventListener("click", ()=>{
        let loaderSpace = document.createElement("div")
        loaderSpace.classList.add("w-[15%]", "h-full", "relative", "flex", "justify-center", "items-center")
        let loaderBar = document.createElement("div")
        loaderBar.classList.add("Bar", "rounded-full", "border-[#00E4D8]", "border","absolute" , "w-[3rem]", "h-[3rem]")
        loaderSpace.appendChild(loaderBar)
        let divHotPot = document.createElement("div")
        divHotPot.classList.add("hotPotsMessage", "flex", "gap-x-1", "mt-3")
        let message = document.createElement("p")
        message.classList.add("select-none")
        message.appendChild(document.createTextNode("Generating the plots...\n You will be redirected when they are generated."))
        divHotPot.appendChild(loaderSpace)
        divHotPot.appendChild(message)
        if(filtersSection.children.length <= 2){
            filtersSection.appendChild(divHotPot)
        }
        generateHotPlots()
    })
    filtersSection.appendChild(buttonHotPlot)
}
/**
 * Function to create the filter form and the inputs inside it
 */
const loadFilters = ()=>{
    let form = document.createElement("form")
    form.classList.add("mt-3", "w-full", "flex", "flex-col", "gap-y-3")
    /**
     * Operation filter and options creation
     */
    let divOperation = document.createElement("div")
    divOperation.classList.add("flex", "gap-x-2", "justify-center")
    let operationLabel = document.createElement("label")
    operationLabel.appendChild(document.createTextNode("Operation: "))
    operationLabel.setAttribute("for", "operation")
    let operationInput = document.createElement("select")
    operationInput.setAttribute("name", "operation")
    operationInput.setAttribute("id", "operation")
    operationInput.classList.add("w-[6.25rem]", "border-[#325D88]", "border-[0.15rem]", "bg-white", "border-opacity-50")
    let defaultOperation = document.createElement("option")
    defaultOperation.appendChild(document.createTextNode("All"))
    defaultOperation.setAttribute("selected", undefined)
    defaultOperation.setAttribute("value", "All")
    operationInput.appendChild(defaultOperation)
    let types = filters.types
    types.forEach(type => {
        let option = document.createElement("option")
        option.setAttribute("value", type)
        option.appendChild(document.createTextNode(type))
        operationInput.appendChild(option)
    });
    divOperation.appendChild(operationLabel)
    divOperation.appendChild(operationInput)
    operationInput.addEventListener("change", ()=>{
        if(operationInput.value != "All"){
            dataFiltered = generalData.data.filter((element)=> element.type == operationInput.value)
            dateInput.innerHTML = ""
            dateInput.appendChild(defaultDate)
            timeInput.innerHTML = ""
            timeInput.appendChild(defaultTime)
            dataFiltered[0].data.forEach(element =>{
                if(dateInput.children.length == 0){
                    let option = document.createElement("option")
                    option.setAttribute("value", element.Sdate)
                    option.appendChild(document.createTextNode(element.Sdate))
                    dateInput.appendChild(option)
                }else{
                    let foundElements = [].slice.call(dateInput.children).filter(currentElement=> currentElement.value == element.Sdate)
                    if(foundElements.length == 0){
                        let option = document.createElement("option")
                        option.setAttribute("value", element.Sdate)
                        option.appendChild(document.createTextNode(element.Sdate))
                        dateInput.appendChild(option)
                    }
                }
            })
        }else{
            resetFilters(dateInput, defaultDate, timeInput, defaultTime)
        }
    })
    /**
     * Date and time filters creation
     */
    let divDateTime = document.createElement("div")
    divDateTime.classList.add("flex", "justify-evenly")
    let divDate = document.createElement("div")
    divDate.classList.add("flex", "gap-x-2")
    let dateLabel = document.createElement("label")
    dateLabel.appendChild(document.createTextNode("Date: "))
    dateLabel.setAttribute("for", "date")
    let dateInput = document.createElement("select")
    dateInput.setAttribute("name", "date")
    dateInput.setAttribute("id", "date")
    dateInput.classList.add("w-[8.125rem]", "border-[#325D88]", "border-[0.15rem]", "bg-white", "border-opacity-50")
    let defaultDate = document.createElement("option")
    defaultDate.appendChild(document.createTextNode("All"))
    defaultDate.setAttribute("selected", undefined)
    defaultDate.setAttribute("value", "All")
    dateInput.appendChild(defaultDate)
    let dates = filters.dates
    dates.forEach(date => {
        let option = document.createElement("option")
        option.setAttribute("value", date)
        option.appendChild(document.createTextNode(date))
        dateInput.appendChild(option)
    });
    divDate.appendChild(dateLabel)
    divDate.appendChild(dateInput)
    let divTime = document.createElement("div")
    divTime.classList.add("flex", "gap-x-2")
    let timeLabel = document.createElement("label")
    timeLabel.appendChild(document.createTextNode("Time: "))
    timeLabel.setAttribute("for", "time")
    let timeInput = document.createElement("select")
    timeInput.setAttribute("name", "time")
    timeInput.setAttribute("id", "time")
    timeInput.classList.add("w-[8.125rem]", "border-[#325D88]", "border-[0.15rem]", "bg-white", "border-opacity-50")
    let defaultTime = document.createElement("option")
    defaultTime.appendChild(document.createTextNode("Select a date"))
    defaultTime.setAttribute("selected", undefined)
    defaultTime.setAttribute("value", "All")
    timeInput.appendChild(defaultTime)
    divTime.appendChild(timeLabel)
    divTime.appendChild(timeInput)
    divDateTime.appendChild(divDate)
    divDateTime.appendChild(divTime)
    /**
     * Time options on date selection
     */
    dateInput.addEventListener("change", ()=>{
        if(dateInput.value != "All"){
            timeInput.innerHTML = ""
            if(operationInput.value == "All"){
                filters.times[dateInput.value].forEach(time => {
                    let option = document.createElement("option")
                    option.setAttribute("value", time.Time)
                    option.appendChild(document.createTextNode(time.Time))
                    timeInput.appendChild(option)
                })
            }else{
                let filteredTimes = structuredClone(generalData.data.filter((element)=> element.type == operationInput.value))
                filteredTimes = filteredTimes[0].data.filter((element)=> element.Sdate == dateInput.value)
                for (let i = 0; i < filteredTimes.length; i++) {
                    let option = document.createElement("option")
                    option.setAttribute("value", filteredTimes[i].Etime)
                    option.appendChild(document.createTextNode(filteredTimes[i].Etime))
                    timeInput.appendChild(option)
                }

            }
        }else{
            timeInput.innerHTML = ""
            timeInput.appendChild(defaultTime)
        }
    })
    /**
     * Buttons creation
     */
    let buttons = document.createElement("div")
    buttons.classList.add("flex", "justify-evenly")
    let filterButton = document.createElement("button")
    filterButton.classList.add("hover:bg-[#325D88]", "bg-[#6585a6]", "text-white", "font-semibold", "p-2", "rounded-lg", "border-[#325D88]", "border-2", "mt-3", "w-[45%]", "self-center")
    filterButton.appendChild(document.createTextNode("Filter data"))
    filterButton.addEventListener("click", (e)=>{
        e.preventDefault()
        if(operationInput.value != "All" && dateInput.value != "All" && timeInput.value != "All"){
            selectedFilters["operation"] = operationInput.value
            selectedFilters["date"] = dateInput.value
            selectedFilters["time"] = timeInput.value
            if(divLogs.classList.contains("bg-[#325D88]")){
                let evento = new Event("click")
                divLogs.dispatchEvent(evento)
            }
            if(selectedFilters["operation"] != "All"){
                hideOrRevealCards(selectedFilters["operation"], "hide")
            }
        }else{
            if(operationInput.value != "All" && dateInput.value == "All" && timeInput.value == "All"){
                selectedFilters["operation"] = operationInput.value
                selectedFilters["date"] = dateInput.value
                selectedFilters["time"] = timeInput.value
                filteredData = generalData.data.filter((element) => selectedFilters["operation"] == element.type)
                if(divLogs.classList.contains("bg-[#325D88]")){
                    let evento = new Event("click")
                    divLogs.dispatchEvent(evento)
                }
                hideOrRevealCards(selectedFilters["operation"], "hide")
            }else if(operationInput.value == "All" && dateInput.value != "All" && timeInput.value != "All"){
                selectedFilters["date"] = dateInput.value
                selectedFilters["time"] = timeInput.value
                if(divLogs.classList.contains("bg-[#325D88]")){
                    let evento = new Event("click")
                    divLogs.dispatchEvent(evento)
                }
                hideOrRevealCards(selectedFilters["operation"], "show")
            }else{
                selectedFilters = {}
                divContent.classList.remove("overflow-y-scroll")
                setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
                if(divLogs.classList.contains("bg-[#325D88]")){
                    printAllLogs()
                }
                hideOrRevealCards(selectedFilters["operation"], "show")
            }
        }
    })
    let clearButton = document.createElement("button")
    clearButton.classList.add("hover:bg-[#325D88]", "bg-[#6585a6]", "text-white", "font-semibold", "p-2", "rounded-lg", "border-[#325D88]", "border-2", "mt-3", "w-[45%]", "self-center")
    clearButton.appendChild(document.createTextNode("Restore defaults"))
    clearButton.addEventListener("click", (e)=>{
        e.preventDefault()
        selectedFilters = {}
        operationInput.selectedIndex = 0
        resetFilters(dateInput, defaultDate, timeInput, defaultTime)
        divContent.classList.remove("overflow-y-scroll")
        setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
        if(divLogs.classList.contains("bg-[#325D88]")){
           printAllLogs()
        }
        hideOrRevealCards("All", "show")
    })

    buttons.appendChild(filterButton)
    buttons.appendChild(clearButton)
    form.appendChild(divOperation)
    form.appendChild(divDateTime)
    form.appendChild(buttons)
    sectionBody.appendChild(form)
    filtersCard.appendChild(sectionTitle)
    filtersCard.appendChild(sectionBody)
}
/**
 * Function that represents all the operation cards in the right div. Inside each card there are iframes representing interactive plots
 */
const showAllData = (data)=>{
    let graphicContents = document.querySelector("div.graphicSection")
    if( graphicContents == null){
        graphicContents = document.createElement("div")
        graphicContents.classList.add("w-[90%]", "flex", "flex-col", "gap-y-3", "self-center", "graphicSection")
    }else{
        graphicContents.innerHTML = "" 
    }
    data.forEach(element => {
        let card = document.createElement("div")
        card.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", element.type)
        let title = document.createElement("h3")
        title.appendChild(document.createTextNode(element.type))
        title.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
        let histograms = document.createElement("section")
        histograms.classList.add("flex", "flex-col", "gap-y-2", "my-2")
        let imageArray = [...element.file]
        imageArray.sort((a,b)=>{return a.length - b.length})
        for (let i = 0; i < imageArray.length; i++) {   
            let newIframe = document.createElement("iframe")
            newIframe.setAttribute("src", URLPath+imageArray[i])
            newIframe.setAttribute("loading", "lazy")
            newIframe.classList.add("w-[95%]", "h-[25rem]", "self-center")
            if(!imageArray[i].includes("torque") && !imageArray[i].includes("Diff")){
                newIframe.classList.add("order-1")
            }else if(!imageArray[i].includes("Diff")){
                newIframe.classList.add("order-2")
            }else{
                newIframe.classList.add("order-3")
            }
            histograms.appendChild(newIframe)
        }

        card.appendChild(title)
        card.appendChild(histograms)
        graphicContents.appendChild(card)
    });
    contenSection.appendChild(graphicContents)
}
/**
 * Function that restores the default appeareance of the website restoring all the filters and showing the hidden cards
 * @param {*} dateInput HTML Element filter for the date input
 * @param {*} defaultDate Value of the default date => "All"
 * @param {*} timeInput HTML Element filter for the time input
 * @param {*} defaultTime Value of the default time => "All"
 */
const resetFilters = (dateInput, defaultDate,  timeInput, defaultTime)=>{
    dateInput.innerHTML = ""
    dateInput.appendChild(defaultDate)
    let dates = filters.dates
    dates.forEach(date => {
        let option = document.createElement("option")
        option.setAttribute("value", date)
        option.appendChild(document.createTextNode(date))
        dateInput.appendChild(option)
    });
    timeInput.innerHTML = ""
    timeInput.appendChild(defaultTime)

}
/**
 * Function that adds the interactive buttons around the date input, this also generates the interactivity (Navigating through the dates and searching) and calls other functions to continue fetching the new information.
 */
const startInputButtons = ()=>{
    let div = document.querySelector("div.dateInput")
    if(div.children.length == 2){
        div.classList.add("flex", "flex-row", "items-center", "gap-x-1")
        let backButton = document.createElement("button")
        backButton.classList.add("rounded-xl", "bg-[#325D88]", "back")
        let buttonImage = document.createElement("img")
        buttonImage.setAttribute("src", URLPath+"static/img/arrow.svg")
        buttonImage.classList.add("size-6", "rotate-180")
        backButton.appendChild(buttonImage)
        let fowardButton = document.createElement("button")
        fowardButton.classList.add("rounded-xl", "bg-[#325D88]", "foward")
        let buttonImage2 = document.createElement("img")
        buttonImage2.setAttribute("src", URLPath+"static/img/arrow.svg")
        buttonImage2.classList.add("size-6")
        fowardButton.appendChild(buttonImage2)
        let searchButton = document.createElement("button")
        searchButton.classList.add("rounded-xl", "bg-[#325D88]", "search")
        let buttonImage3 = document.createElement("img")
        buttonImage3.setAttribute("src", URLPath+"static/img/searchNew.svg")
        buttonImage3.classList.add("size-6", "p-1")
        searchButton.appendChild(buttonImage3)
        div.appendChild(backButton)
        div.appendChild(fowardButton)
        div.appendChild(searchButton)
        let divChilds = [...div.children]
        input = null
        divChilds.forEach(child => {
            switch (true) {
                case child.classList.contains("back"):
                    child.classList.add("order-1")
                    break;
                case child.classList.contains("subtitle"):
                    child.classList.add("order-2")
                    break;
                case child.classList.contains("input"):
                    child.classList.add("order-3")
                    input = child
                    break;
                case child.classList.contains("foward"):
                    child.classList.add("order-4")
                    break;
                case child.classList.contains("search"):
                    child.classList.add("order-5")
                    break;
            
            }
        });
        let url = currentUrl.split("/")
        if(url.length == 4){
            if(!currentUrl.includes("/"+url[url.length-1]+"/?date="+input.value)){
                history.pushState({date: input.value}, "", "/"+url[url.length-1]+"/?date="+input.value)
            }
        }else{
            if(!currentUrl.includes("/"+url[url.length-2]+"/?date="+input.value) && history.state != null){
                history.replaceState({date: input.value}, "", "/"+url[url.length-2]+"/?date="+input.value)
            }else{
                history.pushState({date: input.value}, "", "/"+url[url.length-2]+"/?date="+input.value)
            }
        }
        updateAnchorHref()
        backButton.addEventListener("click", ()=>{
            let value = input.value
            let newDate = new Date(value)
            newDate.setDate(newDate.getDate()-1)
            input.valueAsDate = newDate
        })
        fowardButton.addEventListener("click", ()=>{
            let value = input.value
            let newDate = new Date(value)
            newDate.setDate(newDate.getDate()+1)
            input.valueAsDate = newDate
        })
        searchButton.addEventListener("click", ()=>{
            let value = input.value
            if(Object.keys(generalData).length > 0){
                if(generalData.data[0] != undefined){
                    if(value != generalData.data[0].data[0]["Sdate"]){
                        changeTitleAndFetch(value)
                    }
                }else{
                    changeTitleAndFetch(value)
                }
            }else{
               changeTitleAndFetch(value)
            }
        })
    }
}
/**
 * This function changes the title and fetches the new information when the date input is changed and the search button is pressed
 * @param {*} value This is the new value of the date input
 */
const changeTitleAndFetch = (value)=>{
    runLoader()
    titleParts = title.innerHTML.split("-")
    title.innerHTML = ""
    title.appendChild(document.createTextNode(titleParts[0]+"-"+titleParts[1]+"-"+value))
    let url = currentUrl.split("/")
    if(history.state == null){
        if(!currentUrl.includes("/"+url[url.length-1]+"/?date="+value)){
            history.pushState({date: value}, "", "/"+url[url.length-1]+"/?date="+value)
        }
    }else{
        if(!currentUrl.includes("/"+url[url.length-2]+"/?date="+value)){
            history.replaceState({date: value}, "", "/"+url[url.length-2]+"/?date="+value)
        }
    }
    updateAnchorHref()
    fetchLatestData(value)
    setTimeout(deactivateLoader, 1000)
}
/**
 * Function that starts the plot sections, it generates the cables representation, the 10X cables and the 20X cables sections on the Load Pins Website
 */
const startPlotSections = ()=>{
    plotSection = document.querySelector("div.plotsArea")
    plotSection.classList.add("flex", "flex-col", "items-center")
    plotSection.innerHTML = ""
    let plotSec1 = document.createElement("div")
    plotSec1.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", "cablesImages", "w-auto")
    let image1 = document.createElement("img")
    image1.setAttribute("src", "/static/img/LST-Figure-10X.png")
    image1.classList.add("h-[27.5rem]")
    let image2 = document.createElement("img")
    image2.setAttribute("src", "/static/img/LST-Figure-20X.png")
    image2.classList.add("h-[27.5rem]")
    let divImages = document.createElement("div")
    divImages.classList.add("flex", "justify-center", "gap-x-3")
    divImages.appendChild(image2)
    divImages.appendChild(image1)
    let title = document.createElement("h3")
    title.appendChild(document.createTextNode("Cables representation"))
    title.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
    plotSec1.appendChild(title)
    plotSec1.appendChild(divImages)
    let plotSec2 = document.createElement("div")
    plotSec2.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", "hundred", "w-full")
    let title2 = document.createElement("h3")
    title2.appendChild(document.createTextNode("10X Cables"))
    title2.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
    plotSec2.appendChild(title2)
    let plotSec3 = document.createElement("div")
    plotSec3.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", "twoHundred", "w-full")
    let title3 = document.createElement("h3")
    title3.appendChild(document.createTextNode("20X Cables"))
    title3.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
    plotSec3.appendChild(title3)
    plotSection.appendChild(plotSec1)
    plotSection.appendChild(plotSec2)
    plotSection.appendChild(plotSec3)
}
/**
 * Function that shows or hides the sections when filter is applied or filters are cleared
 * @param {*} type Is the operation type, coul be: "Track", "Park-in", "Park-out" or "GoToPos"
 * @param {*} option could be either "show" or "hide"
 */
const hideOrRevealCards = (type, option)=>{
    let graphicSection = document.querySelector("div.graphicSection")
    let GSChilds = [...graphicSection.children]
    switch(true){
        case option == "hide":
            GSChilds.forEach(child => {
                if(!child.classList.contains(type)){
                    if(!child.classList.contains("hidden")){
                        child.classList.add("hidden")
                    }
                }else{
                    if(child.classList.contains("hidden")){
                        child.classList.remove("hidden")
                    }
                }
            });
            break
        case option == "show":
            GSChilds.forEach(child => {
                if(!child.classList.contains(type)){
                    if(child.classList.contains("hidden")){
                        child.classList.remove("hidden")
                    }
                }else{
                    if(child.classList.contains("hidden")){
                        child.classList.remove("hidden")
                    }
                }
            });
            break
    }
}
/**
 * Function that creates an iframe and references each one the array strings loading the interactive plots
 * @param {*} array It contains two strings which are the urls for the interactive plots
 */
const showLoadPins = (array) =>{
    array.forEach(element => {
        let plotDiv = document.createElement("div")
        plotDiv.classList.add("flex")
        let newIframe = document.createElement("iframe")
        newIframe.setAttribute("src", URLPath+element)
        newIframe.classList.add("w-[100%]", "h-[27.5rem]", "self-center")
        plotDiv.appendChild(newIframe)
        if (element.includes("10X")){
            let hundredCables = document.querySelector("div.hundred")
            hundredCables.appendChild(plotDiv)
        }else{
            let twoHundredCables = document.querySelector("div.twoHundred")
            twoHundredCables.appendChild(plotDiv)
        }
    })
}
/**
 * Function that refresh the anchor (DriveMonitoring, and Load Pin navigation buttons) hrefs to the new date selected
 */
const updateAnchorHref = ()=>{
    let driveMonitoringButton = document.querySelector(".driveMonitoring")
    let driveMonHref = driveMonitoringButton.href
    if(!driveMonHref.includes("date")){
        driveMonitoringButton.href = driveMonitoringButton.href+"/?date="+history.state["date"]
    }else{
        driveMonitoringButton.href = driveMonHref.replace(/=(.)*$/, "="+history.state["date"])
    }
    let loadPinsButton = document.querySelector(".loadPins")
    let loadPinsHref = loadPinsButton.href
    if(!loadPinsHref.includes("date")){
        loadPinsButton.href = loadPinsButton.href+"/?date="+history.state["date"]
    }else{
        loadPinsButton.href = loadPinsHref.replace(/=(.)*$/, "="+history.state["date"])
    }
}
/**
 * Function that check if the modal is being displayed
 * @returns True if the modal is being displayed or false if it is not
 */
const checkLoader = ()=>{
    let foundModal = document.querySelector("div.modal")
    return foundModal != null
}
window.onload = ()=>{
    setTimeout(()=>{
        if(checkLoader()){
            deactivateLoader()
        }
    }, 1000)
}

/**
 * Function that creates the "Return to top" button and adds the functionalities to it
 */
const createTopButton = ()=>{
    let topButton = document.createElement("div")
    topButton.classList.add("w-[4rem]", "fixed", "flex", "justify-center", "bottom-3", "right-3", "hover:bg-[#325D88]", "bg-[#6585a6]", "text-white", "font-semibold", "p-2", "rounded-lg", "border-[#325D88]", "border-2", "mt-3", "hidden", "translate-y-[15rem]")
    let buttonImage = document.createElement("img")
    buttonImage.setAttribute("src", URLPath+"static/img/arrow.svg")
    buttonImage.classList.add("size-8", "-rotate-90", "select-none", "pointer-events-none")
    topButton.appendChild(buttonImage)
    topButton.addEventListener("click", ()=>{
        window.scrollTo({top: 0, left: 0, behavior: "smooth"})
    })
    window.addEventListener("scroll", ()=>{
        if(window.scrollY > 100){
            if(topButton.classList.contains("hidden")){
                if(topButton.classList.contains("slideDown")){
                    topButton.classList.remove("slideDown")
                }
                topButton.classList.remove("hidden")
                topButton.classList.add("slideUp")
                topButton.classList.remove("translate-y-[15rem]")
                
            }
        }else{
            if(!topButton.classList.contains("hidden")){
                if(topButton.classList.contains("slideUp")){
                    topButton.classList.remove("slideUp")
                }
                topButton.classList.add("slideDown")
                topButton.classList.add("translate-y-[15rem]")
                setTimeout(()=>{topButton.classList.add("hidden")}, 300)
            }
        }
    })
    body.appendChild(topButton)
}
const generateHotPlots = async()=>{
    let response = await fetch("http://127.0.0.1:8000/storage/generateHotPlots")
    .then((res)=> res.json())
    if(response.Message == null){
        if(response.status == 123423){
            window.location.replace("http://127.0.0.1:8000/driveMonitoring")
        }else{
            console.log(response.status)
        }
    }else{
        let foundHotPotLoader = document.querySelector(".hotPotsMessage")
        foundHotPotLoader.innerHTML = ""
        let newMessage = document.createElement("p")
        newMessage.appendChild(document.createTextNode(response.Message))
        newMessage.classList("text-red-500")
    }
}