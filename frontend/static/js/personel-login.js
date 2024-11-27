document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("personelLoginForm"); // Form id'sini personel login formuna göre değiştiriyoruz.

    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            try {
                const response = await fetch("http://127.0.0.1:8000/api/token/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ username, password }),
                });

                if (response.ok) {
                    const data = await response.json();
                    const accessToken = data.access;
                    localStorage.setItem("accessToken", accessToken); // Tokeni localStorage'a kaydediyoruz.

                    const payload = JSON.parse(atob(accessToken.split('.')[1]));
                    // Role'ü kontrol ediyoruz.
                    if (payload.role === 'personel') {
                        alert("Personel giriş başarılı!");
                        window.location.href = "/user/personel/dashboard/";
                    } else {
                        alert("Bu sayfaya yalnızca personeller giriş yapabilir.");
                    }
                } else {
                    alert("Giriş başarısız! Kullanıcı adını veya şifrenizi kontrol edin.");
                }
            } catch (error) {
                alert("Bir hata oluştu: " + error.message);
            }
        });
    } else {
        console.error("Form öğesi bulunamadı.");
    }
});

 
