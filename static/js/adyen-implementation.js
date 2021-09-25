const clientKey = JSON.parse(document.getElementById('client-key').innerHTML);
const chosenCountry = JSON.parse(document.getElementById('country_code').innerHTML);

async function initCheckout() {
    const paymentMethodsResponse = await callServer('/api/getPaymentMethods', {chosenCountry});
    const configuration = {
     paymentMethodsResponse: paymentMethodsResponse, // The `/paymentMethods` response from the server.
     clientKey, // Web Drop-in versions before 3.10.1 use originKey instead of clientKey.
     locale: "en-US",
     environment: "test",
     onSubmit: (state, dropin) => {
         // Global configuration for onSubmit
         // Your function calling your server to make the `/payments` request
        postData('/api/initiatePayment', state.data, dropin);

     },
     onAdditionalDetails: (state, dropin) => {
       // Your function calling your server to make a `/payments/details` request
       postData('/api/makeDetailsCall', state.data, dropin);
     },
     paymentMethodsConfiguration: {
       card: { // Example optional configuration for Cards
         hasHolderName: true,
         holderNameRequired: true,
         enableStoreDetails: true,
         name: 'Credit or debit card',
         billingAddressRequired: true
       },
       threeDS2: { // Web Components 4.0.0 and above: sample configuration for the threeDS2 action type
                     challengeWindowSize: '05'
                      // Set to any of the following:
                      // '02': ['390px', '400px'] -  The default window size
                      // '01': ['250px', '400px']
                      // '03': ['500px', '600px']
                      // '04': ['600px', '400px']
                      // '05': ['100%', '100%']
        }
     }
    };
    const checkout = new AdyenCheckout(configuration);

    const dropin = checkout
        .create('dropin', {
        // Starting from version 4.0.0, Drop-in configuration only accepts props related to itself and cannot contain generic configuration like the onSubmit event.
            openFirstPaymentMethod:false
        })
       .mount('#dropin-container');
};


async function callServer(url, data) {
	const res = await fetch(url, {method: "POST",  headers: {'Accept': 'application/json','Content-Type': 'application/json'},body: data ? JSON.stringify(data) : "",});
	return await res.json();
}

async function postData(url, data, dropin) {
    try {
        let response = await fetch(url, {method: "POST",  headers: {'Accept': 'application/json','Content-Type': 'application/json'},body: data ? JSON.stringify(data) : "",});
        let responseJson = await response.json();
        alert(responseJson);
        if(responseJson.action){
            dropin.handleAction(responseJson.action);
        }
        else{
            if(responseJson.resultCode == "Authorised"){
                window.location.href = "/checkout-success?result="+JSON.stringify(responseJson);
            }
            else{
               window.location.href = "/checkout-failed?result="+JSON.stringify(responseJson.refusalReason);
            }
        }
    } catch(error) {
        console.error(error);
    }
}




initCheckout();