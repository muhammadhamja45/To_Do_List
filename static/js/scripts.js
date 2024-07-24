document.addEventListener("DOMContentLoaded", () => {
    const addTaskButton = document.getElementById("add-task-button");
    const addTaskForm = document.getElementById("add-task-form");
    const todayButton = document.getElementById("today-button");
    const prevWeekButton = document.getElementById("prev-week");
    const nextWeekButton = document.getElementById("next-week");
    const dateSlider = document.getElementById("date-slider");
    const monthYearDisplay = document.getElementById("month-year");

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
            const dateItem = document.createElement("div");
            dateItem.className = "p-2 cursor-pointer";
            dateItem.dataset.date = date.toISOString().split("T")[0];
            dateItem.innerHTML = `
                <div class="text-center">
                    <div class="text-sm">${date.toLocaleDateString("en-US", { weekday: "short" })}</div>
                    <div class="text-lg font-bold">${date.getDate()}</div>
                    <div class="text-sm">${date.toLocaleDateString("en-US", { month: "short" })}</div>
                </div>
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
        if (e.target.closest("[data-date]")) {
            const selectedDate = e.target.closest("[data-date]").dataset.date;
            fetchTasks(selectedDate);
        }
    });

    renderDates(currentStartDate);
});
