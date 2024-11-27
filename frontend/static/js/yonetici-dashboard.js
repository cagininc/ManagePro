document.addEventListener("DOMContentLoaded", () => {
    // Hoşgeldiniz mesajını ayarla
    const token = localStorage.getItem("accessToken");
    const welcomeMessage = document.getElementById("welcomeMessage");

    if (token) {
        const payload = JSON.parse(atob(token.split(".")[1])); // Token'dan bilgileri çöz
        const username = payload.username || "Yönetici";
        welcomeMessage.textContent = `Hoşgeldiniz, ${username}`;
    } else {
        welcomeMessage.textContent = "Hoşgeldiniz";
    }

    // Logout butonu
    const logoutButton = document.getElementById("logout");
    logoutButton.addEventListener("click", (event) => {
        event.preventDefault();
        localStorage.removeItem("accessToken");
        window.location.replace("/");
    });

    // Tablar ve içerikler
    const attendanceTab = document.getElementById("attendanceTab");
    const leaveRequestsTab = document.getElementById("leaveRequestsTab");
    const attendanceContent = document.getElementById("attendanceContent");
    const leaveRequestsContent = document.getElementById("leaveRequestsContent");

    // Tüm tab içeriklerini gizleyen fonksiyon
    const hideAllTabs = () => {
        attendanceContent.classList.add("hidden");
        leaveRequestsContent.classList.add("hidden");
    };

    // Tab seçimini değiştiren fonksiyon
    const activateTab = (activeTab, inactiveTab) => {
        activeTab.classList.add("bg-white", "text-blue-500");
        activeTab.classList.remove("bg-gray-300", "text-gray-500");
        inactiveTab.classList.add("bg-gray-300", "text-gray-500");
        inactiveTab.classList.remove("bg-white", "text-blue-500");
    };

    // Tab event listener'ları
    attendanceTab.addEventListener("click", () => {
        hideAllTabs();
        attendanceContent.classList.remove("hidden");
        activateTab(attendanceTab, leaveRequestsTab);

        // Giriş-Çıkış tablosunu güncelle
        $('#attendanceTable').DataTable().ajax.reload();
    });

    leaveRequestsTab.addEventListener("click", () => {
        hideAllTabs();
        leaveRequestsContent.classList.remove("hidden");
        activateTab(leaveRequestsTab, attendanceTab);

        // İzin talepleri tablosunu güncelle
        updateLeaveRequestsTable();
    });

    // Varsayılan olarak ilk tabı göster
    hideAllTabs();
    attendanceContent.classList.remove("hidden");
    activateTab(attendanceTab, leaveRequestsTab);

    // Giriş-Çıkış tablosu için DataTable ayarları
    $('#attendanceTable').DataTable({
        serverSide: true,
        processing: true,
        ajax: {
            url: "http://127.0.0.1:8000/api/attendance/datatable/",
            type: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
            dataSrc: "data",
        },
        columns: [
            { data: "user" },
            { data: "date" },
            { data: "check_in" },
            { data: "check_out" },
            { data: "office_duration" },
            { data: "late_duration" },
        ],
        language: {
            processing: "<span class='text-blue-500'>Lütfen bekleyin, veriler yükleniyor...</span>",
        },
    });

    // İzin talepleri tablosunu güncelleyen fonksiyon
    function updateLeaveRequestsTable() {
        // Eğer tablo zaten oluşturulmuşsa, önce yok et
        if ($.fn.DataTable.isDataTable('#leaveRequestsTable')) {
             $('#leaveRequestsTable').DataTable().clear().destroy();

        }

        // Yeni DataTable oluştur
        const leaveTable = $('#leaveRequestsTable').DataTable({
            serverSide: true,
            processing: true,
            ajax: {
                url: "http://127.0.0.1:8000/api/leave/requests/",
                type: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
                dataSrc: "data",
            },
            columns: [
                { data: "id" },
                { data: "username" },
                { data: "start_date" },
                { data: "end_date" },
                { data: "status" },
                { data: "reason" },
                {data:"remaining_leave_days"},
                {
                    data: null,
                    render: (data, type, row) => {
                        return `
                            <button class="approve-button bg-green-500 text-white px-2 py-1 text-xs rounded-full">Onayla</button>
                            <button class="reject-button bg-red-500 text-white px-2 py-1 text-xs rounded-full">Reddet</button>
                        `;
                    },
                },
            ],
            language: {
                processing: "<span class='text-blue-500'>Lütfen bekleyin, veriler yükleniyor...</span>",
            },
        });

        // Event Listener düğmeler(onayla ve reddet)
        $('#leaveRequestsTable tbody').on('click', '.approve-button', function () {
            const rowData = leaveTable.row($(this).parents('tr')).data();
            handleLeaveAction(rowData.id, "approved");
        });

        $('#leaveRequestsTable tbody').on('click', '.reject-button', function () {
            const rowData = leaveTable.row($(this).parents('tr')).data();
            handleLeaveAction(rowData.id, "rejected");
        });
    }

    // İzin talebi durumu değiştirme fonksiyonu
    function handleLeaveAction(leaveId, newStatus) {
        fetch(`http://127.0.0.1:8000/api/leave/update/${leaveId}/`, {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ status: newStatus }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Durum güncellenemedi");
                }
                return response.json();
            })
            .then((data) => {
                alert(data.message);
                // updateLeaveRequestsTable(); // Tabloyu güncelle
                //sadece satırı değiştiriyoruz
                const updatedLeave = data.updated_leave;
        leaveTable.row($(`#leaveRequestsTable tbody tr:has(button[data-id="${updatedLeave.id}"])`))
            .data(updatedLeave)
            .draw(false); //
            })
            .catch((error) => {
                console.error(error);
                alert("Bir hata oluştu");
            });
    }
});
