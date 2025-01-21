document.addEventListener("DOMContentLoaded", () => {
    const queryInput = document.getElementById("query");
    const searchBtn = document.getElementById("search-btn");
    const resultsTable = document.getElementById("results");
    const locationFilter = document.getElementById("location-filter");
    const universityFilter = document.getElementById("university-filter");
    const yearFilter = document.getElementById("year-filter");
    const filterBtn = document.getElementById("filter-btn");
    const loginBtn = document.getElementById("login-btn");
    const registerBtn = document.getElementById("register-btn");
    const logoutBtn = document.getElementById("logout-btn");
    const loginModal = document.getElementById("login-modal");
    const registerModal = document.getElementById("register-modal");
    const closeModal = document.getElementById("close-modal");
    const closeRegisterModal = document.getElementById("close-register-modal");
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const welcomeMessage = document.getElementById("welcome-message");
    const recommendationsDiv = document.getElementById("recommendation-list");

    const fetchFilters = async () => {
        try {
            const response = await fetch('/filters');
            const data = await response.json();

            data.locations.forEach(location => {
                const option = document.createElement("option");
                option.value = location;
                option.textContent = location;
                locationFilter.appendChild(option);
            });

            data.universities.forEach(university => {
                const option = document.createElement("option");
                option.value = university;
                option.textContent = university;
                universityFilter.appendChild(option);
            });

            data.years.forEach(year => {
                const option = document.createElement("option");
                option.value = year;
                option.textContent = year;
                yearFilter.appendChild(option);
            });
        } catch (error) {
            console.error("Error fetching filters:", error);
        }
    };

    const fetchResults = async (query, filters = {}) => {
        try {
            const params = new URLSearchParams({ query, ...filters });
            const response = await fetch(`/search?${params}`);
            const results = await response.json();

            resultsTable.querySelector("tbody").innerHTML = "";

            if (results.length === 0) {
                resultsTable.querySelector("tbody").innerHTML = `
                    <tr><td colspan="5">No results found</td></tr>
                `;
                return;
            }

            results.forEach(result => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${result.title}</td>
                    <td>${result.university || "N/A"}</td>
                    <td>${result.location || "N/A"}</td>
                    <td>${result.year || "N/A"}</td>
                    <td><a href="${result.link}" target="_blank">View</a></td>
                `;
                resultsTable.querySelector("tbody").appendChild(row);
            });
        } catch (error) {
            console.error("Error fetching results:", error);
        }
    };

    const fetchRecommendations = async () => {
        const container = document.getElementById("recommendation-container");
        if (!container) {
            console.error("Recommendation container not found");
            return;
        }
    
        try {
            const response = await fetch("/recommendations");
            const recommendations = await response.json();
    
            container.innerHTML = ""; // Clear previous content
    
            if (recommendations.length === 0) {
                container.innerHTML = "<p>No recommendations available.</p>";
                return;
            }
    
            recommendations.forEach((rec) => {
                const card = document.createElement("div");
                card.style.flex = "1";
                card.style.border = "1px solid #ccc";
                card.style.borderRadius = "10px";
                card.style.padding = "10px";
                card.style.backgroundColor = "#f9f9f9";
                card.style.boxShadow = "0px 4px 6px rgba(0, 0, 0, 0.1)";
                card.style.textAlign = "left";
    
                card.innerHTML = `
                    <h3 style="font-size: 1.2em; color: #007bff;">${rec.title}</h3>
                    <p><strong>University:</strong> ${rec.university || "N/A"}</p>
                    <p><strong>Location:</strong> ${rec.location || "N/A"}</p>
                    <p><strong>Year:</strong> ${rec.year || "N/A"}</p>
                    <a href="${rec.link}" style="color: #28a745; font-weight: bold; text-decoration: none;">View</a>
                `;
                container.appendChild(card);
            });
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
    };
    
    
    
    // Fetch recommendations on page load
    fetchRecommendations();
    
    
    
    

    const handleSearch = () => {
        const query = queryInput.value.trim();
        const filters = {
            location: locationFilter.value,
            university: universityFilter.value,
            year: yearFilter.value,
        };

        fetchResults(query, filters);
    };

    searchBtn.addEventListener("click", handleSearch);

    queryInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            handleSearch();
        }
    });

    filterBtn.addEventListener("click", handleSearch);

    registerBtn.addEventListener("click", () => {
        registerModal.style.display = "flex";
    });

    closeRegisterModal.addEventListener("click", () => {
        registerModal.style.display = "none";
    });

    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
    
        const username = document.getElementById("register-username").value;
        const password = document.getElementById("register-password").value;
    
        console.log("Registering with:", { username, password }); // Debug payload
    
        try {
            const response = await fetch("/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });
    
            console.log("Register response status:", response.status); // Debug response status
            const result = await response.json();
            console.log("Register response:", result); // Debug response payload
    
            if (result.success) {
                alert("Registration successful! Please log in.");
                registerModal.style.display = "none";
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Register error:", error); // Log error details
        }
    });
    
    

    loginBtn.addEventListener("click", () => {
        loginModal.style.display = "flex";
    });

    closeModal.addEventListener("click", () => {
        loginModal.style.display = "none";
    });

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const result = await response.json();
            if (result.success) {
                welcomeMessage.textContent = `Welcome, ${username}!`;
                loginModal.style.display = "none";
                loginBtn.style.display = "none";
                registerBtn.style.display = "none";
                logoutBtn.style.display = "inline";
                fetchRecommendations();
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Login error:", error);
        }
    });

    logoutBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/logout", { method: "POST" });
            const result = await response.json();
    
            if (result.success) {
                welcomeMessage.textContent = "";
                loginBtn.style.display = "inline";
                registerBtn.style.display = "inline";
                logoutBtn.style.display = "none";
                
                // Clear recommendations safely
                const recommendationsDiv = document.getElementById("recommendation-container");
                if (recommendationsDiv) {
                    recommendationsDiv.innerHTML = "";  // Ensure it exists before clearing
                }
            }
        } catch (error) {
            console.error("Logout error:", error);
        }
    });
    

    fetchFilters();
    fetchResults("", {});
});
