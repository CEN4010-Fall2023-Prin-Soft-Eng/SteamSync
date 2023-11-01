<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <script
      type="text/javascript"
      src="https://npmcdn.com/parse/dist/parse.min.js"
    ></script>
  </head>
  <body>
    <h1>Steam Account Login</h1>
    <button id="loginButton">Login with Steam</button>
  </body>
  <script>
    // Initialize Parse
    Parse.initialize("QD3o4wcV8jOu1DrPizbXjzTg7tuNZPGoVKyP7RwR", "mad7NPqDFXX0PlkRSITENXZJk2eYzsPcN2Urygoi");
    Parse.serverURL = "https://parseapi.back4app.com/";

    // Steam Web API Key
    const steamApiKey = "E4ABF7871264272AD62B7798CCF512DC";

    // Redirect to Steam login page
    function redirectToSteamLogin() {
      window.location.href = `https://steamcommunity.com/openid/login?openid.ns=http://specs.openid.net/auth/2.0&openid.mode=checkid_setup&openid.return_to=${window.location.href}&openid.realm=${window.location.href}&openid.ns.sreg=http://openid.net/extensions/sreg/1.1&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&openid.identity=http://specs.openid.net/auth/2.0/identifier_select&openid.mode=checkid_setup&openid.ns.ax=http://openid.net/srv/ax/1.0&openid.ax.mode=fetch_request&openid.ax.type.email=http://axschema.org/contact/email&openid.ax.required=email&openid.ax.type.firstname=http://axschema.org/namePerson/first&openid.ax.required=firstname&openid.ax.type.lastname=http://axschema.org/namePerson/last&openid.ax.required=lastname`;
    }

    // Handle the Steam login response
    async function handleSteamLoginResponse() {
      const params = new URLSearchParams(window.location.search);
      const steamOpenId = params.get('openid.identity');
      const steamId = steamOpenId.split('/').pop();
      const response = await fetch(`https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=${steamApiKey}&steamids=${steamId}`);
      const data = await response.json();
      const steamUsername = data.response.players[0].personaname;

      // Use the Steam username to create a new user
      const user = new Parse.User();
      user.set('username', steamUsername);
      user.set('password', 'aDefaultPassword'); // Set a default password for Steam users
      try {
        const newUser = await user.signUp();
        alert(`User logged in successfully: ${newUser.get('username')}`);
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    }

    // Add event listener for the login button
    document.getElementById('loginButton').addEventListener('click', redirectToSteamLogin);

    // Check if the URL contains Steam login response parameters
    if (window.location.search.includes('openid.identity')) {
      handleSteamLoginResponse();
    }
  </script>
</html>
