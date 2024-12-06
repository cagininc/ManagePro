document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("yoneticiLoginForm");

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
                    localStorage.setItem("accessToken", accessToken);//saving token to localstorage

                    const payload = JSON.parse(atob(accessToken.split('.')[1]));
                    // console.log(atob(accessToken.split('.')[1]));

                      //  taking 'role' from token 
                        alert("Yönetici giriş başarılı!");
                         window.location.href = "/user/yonetici/dashboard/";
                   
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
