document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("accessToken");

    if (!token) {
        alert("Giriş yapmalısınız!");
        window.location.href = "/user/personel/login/";
        return;
    }

    // Welcome mesajı
    const payload = JSON.parse(atob(token.split(".")[1]));
    const username = payload.username || "Personel";
    document.getElementById("welcomeMessage").textContent = `Hoşgeldiniz, ${username}`;

    // Tablar ve içerikler
    const attendanceTab = document.getElementById("attendanceTab");
    const leaveTab = document.getElementById("leaveTab");
    const createLeaveTab = document.getElementById("createLeaveTab");

    const attendanceContent = document.getElementById("attendanceContent");
    const leaveContent = document.getElementById("leaveContent");
    const createLeaveContent = document.getElementById("createLeaveContent");

    const tabs = { attendanceTab, leaveTab, createLeaveTab };
    const contents = { attendanceContent, leaveContent, createLeaveContent };

    // Tab geçişlerini kontrol eden fonksiyon
    function hideAllTabs() {
        Object.values(contents).forEach(content => content.classList.add("hidden"));
    }

    function showTab(showContent, activeTab) {
        hideAllTabs();
        showContent.classList.remove("hidden");

        // Tüm tabların vurgulamasını kaldır
        Object.values(tabs).forEach(tab => {
            tab.classList.remove("bg-white", "text-blue-500");
            tab.classList.add("bg-gray-300", "text-gray-500");
        });

        // Aktif tabı vurgula
        activeTab.classList.add("bg-white", "text-blue-500");
        activeTab.classList.remove("bg-gray-300", "text-gray-500");
    }

    // Tab event listeners
    attendanceTab.addEventListener("click", () => {
        showTab(attendanceContent, attendanceTab);
        updateWeeklyAttendanceTable();
    });

    leaveTab.addEventListener("click", () => {
        showTab(leaveContent, leaveTab);
        updateLeaveTable();
    });

    createLeaveTab.addEventListener("click", () => {
        showTab(createLeaveContent, createLeaveTab);
    });

    // Giriş-Çıkış düğmesi
    const officeButton = document.getElementById("officeButton");
    if (officeButton) {
        setupOfficeButton(officeButton);
    }

    // İlk tabloyu yükle
    updateWeeklyAttendanceTable();
});

// Giriş-Çıkış düğmesi için event listener
function setupOfficeButton(officeButton) {
    const token = localStorage.getItem("accessToken");

    officeButton.addEventListener("click", async () => {
        const action = officeButton.textContent.trim();
        const url =
            action === "Ofise Giriş Yap"
                ? "http://127.0.0.1:8000/api/attendance/check_in/"
                : "http://127.0.0.1:8000/api/attendance/check_out/";

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.message);

                // Düğme metnini güncelle
                officeButton.textContent =
                    action === "Ofise Giriş Yap" ? "Ofisten Çıkış Yap" : "Ofise Giriş Yap";

                // Haftalık tabloyu güncelle
                updateWeeklyAttendanceTable();
            } else {
                const errorData = await response.json();
                alert(`Hata: ${errorData.error || "Gün içerisinde ofise giriş yapıldı."}`);
            }
        } catch (error) {
            console.error("Bir hata oluştu:", error);
            alert("Bir hata oluştu. Lütfen tekrar deneyin.");
        }
    });
}

// Haftalık tabloyu güncelleyen fonksiyon
async function updateWeeklyAttendanceTable() {
    const weeklyTableBody = document.querySelector("#weeklyAttendanceTable tbody");

    try {
        const response = await fetch("http://127.0.0.1:8000/api/attendance/weekly/", {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
        });

        if (response.ok) {
            const weeklyRecords = await response.json();

            weeklyTableBody.innerHTML = "";
            weeklyRecords.forEach((record) => {
                const row = `<tr>
                    <td class="border border-gray-300 px-4 py-2">${record.date}</td>
                    <td class="border border-gray-300 px-4 py-2">${record.check_in || "-"}</td>
                    <td class="border border-gray-300 px-4 py-2">${record.check_out || "-"}</td>
                    <td class="border border-gray-300 px-4 py-2">${formatDuration(record.duration)}</td>
                </tr>`;
                weeklyTableBody.innerHTML += row;
            });
        } else {
            console.error("Haftalık tablo verileri alınamadı.");
        }
    } catch (error) {
        console.error("Bir hata oluştu:", error);
    }
}

// İzin tablosunu güncelleyen fonksiyon
async function updateLeaveTable() {
    const leaveTableBody = document.querySelector("#leaveTable tbody");

    try {
        const response = await fetch("http://127.0.0.1:8000/api/leave/list/", {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
        });

        if (response.ok) {
            const leaveRecords = await response.json();

            leaveTableBody.innerHTML = "";
            leaveRecords.forEach((record) => {
                const row = `<tr>
                    <td class="border border-gray-300 px-4 py-2">${record.start_date}</td>
                    <td class="border border-gray-300 px-4 py-2">${record.end_date}</td>
                    <td class="border border-gray-300 px-4 py-2">${record.reason}</td>
                    <td class="border border-gray-300 px-4 py-2 animate-pulse text-blue-600">${record.status}</td>
                </tr>`;
                leaveTableBody.innerHTML += row;
            });
        } else {
            console.error("İzin verileri alınamadı.");
        }
    } catch (error) {
        console.error("Bir hata oluştu:", error);
    }
}

// Süre formatlama fonksiyonu
function formatDuration(durationString) {
    if (!durationString) return "-";

    const durationParts = durationString.split(":");
    const hours = parseInt(durationParts[0], 10);
    const minutes = parseInt(durationParts[1], 10);

    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
}

// İzin Talebi Gönderme
const leaveForm = document.getElementById("leaveForm");
leaveForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const start_date = document.getElementById("start_date").value;
    const end_date = document.getElementById("end_date").value;
    const reason = document.getElementById("reason").value;

    if (!start_date || !end_date || !reason) {
        alert("Tüm alanları doldurunuz.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/leave/create/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
            body: JSON.stringify({ start_date, end_date, reason }),
        });

        if (response.ok) {
            alert("İzin talebiniz başarıyla oluşturuldu.");
            leaveForm.reset(); // Form temizlenir
        } else {
            const errorData = await response.json();
            alert(`Hata: ${errorData.error || "İşlem başarısız."}`);
        }
    } catch (error) {
        console.error("Bir hata oluştu:", error);
        alert("Bir hata oluştu. Lütfen tekrar deneyin.");
    }
});

// Logout butonunu ayarla
const logoutButton = document.getElementById("logout");
logoutButton.addEventListener("click", (event) => {
  event.preventDefault();
  localStorage.removeItem("accessToken");
  window.location.replace("/");
  href = "/";
});