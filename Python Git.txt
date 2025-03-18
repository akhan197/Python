from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import json
import threading
import logging

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Global Order Counter (Sequential Order Numbers)
order_number = 1000  # Start from 1000, increase with each order


def send_to_printer(order_text):
    """ Sends the order text to the printer in a separate thread. """
    try:
        printer_ip = "192.168.1.133"  # Update with your actual printer IP
        printer_port = 9100

        # ESC/POS command for cutting paper (ensures order separation)
        cut_command = "\x1D\x56\x00"

        # Open socket connection to printer
        printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        printer_socket.connect((printer_ip, printer_port))

        # Send receipt text with cut command
        printer_socket.sendall(order_text.encode('utf-8') + cut_command.encode('utf-8'))
        printer_socket.close()

    except Exception as e:
        logging.error(f"Error sending to printer: {e}")


@app.route('/webhook', methods=['POST'])
def webhook():
    global order_number  # Access global order counter

    try:
        data = request.get_json(silent=True)
        logging.debug(f"Received webhook request: {json.dumps(data, indent=2)}")

        if not data or "message" not in data:
            return jsonify({"status": "error", "message": "Invalid webhook format"}), 400

        message = data["message"]

        if message.get("type") == "tool-calls":
            tool_calls = message.get("toolCalls", [])
            for tool in tool_calls:
                if tool["type"] == "function":
                    tool_function = tool.get("function", {})
                    if tool_function.get("name") == "OrderTaker":
                        arguments = tool_function.get("arguments", {})

                        customer_name = arguments.get("customer_name", "Unknown")
                        phone_number = arguments.get("phone_number", "Unknown")
                        order_items = arguments.get("order_items", [])
                        order_type = arguments.get("order_type", "Unknown")  # Collection or Delivery
                        customer_address = arguments.get("customer_address", "N/A") if order_type == "delivery" else ""

                        # Calculate total price (Manual check required for now)
                        item_prices = {
                            "Chicken Burger Meal": 5.99,
                            "Fries": 1.99,
                            "Pizza": 8.99,
                            "Coke": 1.49,
                        }
                        subtotal = sum(item_prices.get(item, 0) for item in order_items)
                        delivery_fee = 1.99 if order_type == "delivery" else 0.00
                        total_price = subtotal + delivery_fee

                        # Increment order number
                        order_number += 1

                        # Format receipt text
                        receipt_text = (
                            "========================\n"
                            "        PEPE’S         \n"
                            "   B8 2AR, Birmingham  \n"
                            "========================\n\n"
                            f"Order #: {order_number}\n"
                            f"Date: 2025-03-18 18:45\n\n"
                            f"Customer: {customer_name}\n"
                            f"Phone: {phone_number}\n"
                            f"Order Type: {order_type.upper()}\n\n"
                            "Items:\n"
                        )

                        for item in order_items:
                            receipt_text += f"- {item}   £{item_prices.get(item, 0):.2f}\n"

                        receipt_text += f"\nSubtotal: £{subtotal:.2f}\n"
                        if order_type == "delivery":
                            receipt_text += f"Delivery Fee: £{delivery_fee:.2f}\n"
                        receipt_text += f"Total: £{total_price:.2f}\n\n"

                        if order_type == "delivery":
                            receipt_text += f"Address: {customer_address}\n"
                            receipt_text += "(Staff: Check if within 3 miles)\n\n"

                        receipt_text += (
                            "========================\n"
                            "   **Pay at Counter**  \n"
                            "========================\n\n"
                            "    THANK YOU!\n"
                            "    Enjoy Your Meal 😊\n"
                            "========================\n"
                        )

                        # Send to printer in a separate thread
                        threading.Thread(target=send_to_printer, args=(receipt_text,)).start()

                        return jsonify({"status": "success", "message": "Order received and sent to printer"}), 200

        elif message.get("type") == "end-of-call-report":
            logging.info(f"Received end-of-call report: {json.dumps(message, indent=2)}")
            return jsonify({"status": "success", "message": "End of call report received"}), 200

        return jsonify({"status": "error", "message": "Unhandled message type"}), 400

    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
