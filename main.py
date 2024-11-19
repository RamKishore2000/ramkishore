import json
import razorpay  # Razorpay client library
import webview
import webbrowser
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

# Razorpay API credentials (Test Mode)
RAZORPAY_KEY_ID = 'rzp_test_hf2afT5lk394ug'
RAZORPAY_KEY_SECRET = 'bSTTNZLyxYZXdNzb2aRUHLvT'

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount_in_paise):
    """
    Function to create an order on Razorpay's server using Razorpay's client library.
    :param amount_in_paise: Amount in paise (100 paise = 1 INR)
    :return: JSON response from Razorpay API
    """
    try:
        # Create an order using Razorpay client
        order_data = client.order.create({
            "amount": amount_in_paise,  # Amount in paise
            "currency": "INR",
            "receipt": "receipt#1",
            "payment_capture": 1  # Automatically capture payment
        })
        print(f"Razorpay Order Creation Response: {order_data}")  # Debugging log
        return order_data
    except Exception as e:
        print(f"Error creating Razorpay order: {str(e)}")
        return None

KV = '''
BoxLayout:
    orientation: "vertical"
    spacing: 10
    padding: 10

    MDLabel:
        text: "Enter the amount for Razorpay Payment"
        theme_text_color: "Secondary"

    MDTextField:
        id: amount_input
        hint_text: "Amount in INR"
        mode: "rectangle"
        input_filter: "int"
        max_text_length: 10
        helper_text: "Enter amount in INR"
        helper_text_mode: "on_focus"

    MDRaisedButton:
        text: "Pay Now"
        on_release: app.pay_now()
'''

class Kishore(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def pay_now(self):
        """
        Function to handle the payment process when 'Pay Now' is clicked.
        It creates an order on Razorpay and shows the Razorpay modal in a WebView.
        """
        # Get the entered amount from the MDTextInput field
        amount_input = self.root.ids.amount_input.text

        if not amount_input:
            # Show an alert dialog if no amount is entered
            dialog = MDDialog(
                title="Error",
                text="Please enter a valid amount",
                size_hint=(0.7, 1)
            )
            dialog.open()
            return

        try:
            # Convert the amount to paise (1 INR = 100 paise)
            amount_in_paise = int(amount_input) * 100
        except ValueError:
            # Show an error dialog if the amount is invalid
            dialog = MDDialog(
                title="Invalid Amount",
                text="Please enter a valid number",
                size_hint=(0.7, 1)
            )
            dialog.open()
            return

        # Create order and get order details from Razorpay API
        order_data = create_razorpay_order(amount_in_paise)
        if order_data:
            order_id = order_data['id']
            amount = order_data['amount']
            currency = order_data['currency']

            # Create Razorpay checkout options in HTML/JavaScript
            checkout_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            </head>
            <body>
                <script>
                    var options = {{
                        key: '{RAZORPAY_KEY_ID}',  // Razorpay API Key
                        amount: {amount},  // Amount in paise (integer)
                        currency: '{currency}',
                        name: 'Your Company',
                        description: 'Test Payment',
                        order_id: '{order_id}',  // Order ID from Razorpay API
                        handler: function(response) {{
                            alert('Payment successful: ' + response.razorpay_payment_id);
                        }} ,
                        modal_error: function(response) {{
                            alert('Payment failed: ' + response.error.description);
                        }},
                        prefill: {{
                            name: 'John Doe',
                            email: 'john.doe@example.com',
                            contact: '9876543210',
                        }},
                        theme: {{
                            color: '#F37254'
                        }}
                    }};
                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                </script>
            </body>
            </html>
            """
            # Open Razorpay checkout in a native window using pywebview
            self.open_payment_modal(checkout_html)

    def open_payment_modal(self, html_content):
        """
        Function to display Razorpay payment modal using pywebview.
        :param html_content: The HTML content that includes the Razorpay checkout script
        """
        # Open Razorpay checkout in a native window
        window = webview.create_window("Razorpay Payment", html=html_content)
        # Set the external link handler
        window.events.external_url = self.open_external_link
        webview.start()

    def open_external_link(self, url):
        """
        Handle external links (like netbanking or UPI) to open in the default browser.
        """
        webbrowser.open(url)

if __name__ == "__main__":
    Kishore().run()
