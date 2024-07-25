document.addEventListener("DOMContentLoaded", () => {
    const addTaskButton = document.getElementById("add-task-button");
    const addTaskForm = document.getElementById("add-task-form");
    const todayButton = document.getElementById("today-button");
    const prevWeekButton = document.getElementById("prev-week");
    const nextWeekButton = document.getElementById("next-week");
    const dateSlider = document.getElementById("date-slider");
    const monthYearDisplay = document.getElementById("month-year");
    const openSidebarButton = document.getElementById("open-sidebar");
    const closeSidebarButton = document.getElementById("close-sidebar");
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("main-content");

    const today = new Date();
    let currentStartDate = new Date(
        today.setDate(today.getDate() - today.getDay() + 1)
    );

    function formatDate(date) {
        const options = { month: "short", day: "numeric", year: "numeric" };
        return date.toLocaleDateString("en-US", options);
    }

    function renderDates(startDate) {
        dateSlider.innerHTML = "";
        for (let i = 0; i < 7; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            const isToday = isSameDate(date, new Date());
            const dateItem = document.createElement("div");
            dateItem.className = `date-item ${isToday ? 'today' : ''}`;
            dateItem.dataset.date = date.toISOString().split("T")[0];
            dateItem.innerHTML = `
                <div class="day">${date.getDate()}</div>
                <div class="weekday">${date.toLocaleDateString("en-US", { weekday: "short" })}</div>
            `;
            dateSlider.appendChild(dateItem);
        }
        updateMonthYearDisplay(startDate);
    }

    function updateWeek(offset) {
        currentStartDate.setDate(currentStartDate.getDate() + offset);
        renderDates(currentStartDate);
    }

    function updateMonthYearDisplay(date) {
        const options = { year: "numeric", month: "long" };
        monthYearDisplay.textContent = date.toLocaleDateString("en-US", options);
    }

    function fetchTasks(date) {
        console.log(`Fetching tasks for date: ${date}`);
    }

    function isSameDate(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    addTaskButton.addEventListener("click", () => {
        addTaskForm.classList.toggle("hidden");
    });

    todayButton.addEventListener("click", () => {
        currentStartDate = new Date(
            today.setDate(today.getDate() - today.getDay() + 1)
        );
        renderDates(currentStartDate);
    });

    prevWeekButton.addEventListener("click", () => {
        updateWeek(-7);
    });

    nextWeekButton.addEventListener("click", () => {
        updateWeek(7);
    });

    dateSlider.addEventListener("click", (e) => {
        if (e.target.closest(".date-item")) {
            const selectedDate = e.target.closest(".date-item").dataset.date;
            fetchTasks(selectedDate);
        }
    });

    openSidebarButton.addEventListener("click", () => {
        sidebar.classList.add("open");
        mainContent.classList.remove("ml-0");
        mainContent.classList.add("ml-64");
    });

    closeSidebarButton.addEventListener("click", () => {
        sidebar.classList.remove("open");
        mainContent.classList.remove("ml-64");
        mainContent.classList.add("ml-0");
    });

    renderDates(currentStartDate);
});


document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    document.body.classList.toggle('dark');
});

document.getElementById('add-task-button').addEventListener('click', function() {
    var form = document.getElementById('add-task-form');
    form.classList.toggle('hidden');
});

AOS.init();