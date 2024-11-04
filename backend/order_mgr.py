from backend.base_manager import Manager as BaseManager

class OrderManager(BaseManager):
    def __init__(self, env):
        super().__init__(env)

    def create_order(self, order, image=None):
        if image is not None:
            # upload image to blob storage
            image_path = f"images/orders/{order.id}.jpg"
            self.blob_db.upload_file(image, image_path, compress=True)
            order.image_path = image_path
        
        self.firestore_db.create_document('orders', order.__dict__)

    def get_order(self, order_id):
        order = self.firestore_db.get_document('orders', order_id)
        return order

    def update_order(self, order_id, updates):
        self.firestore_db.update_document('orders', order_id, updates)

    def delete_order(self, order_id):
        order = self.get_order(order_id)
        if order['image_path']:
            self.blob_db.delete_file(order['image_path'])
        self.firestore_db.delete_document('orders', order_id)

    def get_all_orders(self):
        all_orders = self.firestore_db.get_collection('orders')
        # sort by delivery date
        all_orders.sort(key=lambda x: x['expected_deliver_date'])
        return all_orders

    def create_inventory(self, inventory, image=None):
        if image is not None:
            # upload image to blob storage 
            image_path = f"images/inventory/{inventory.id}.jpg"
            self.blob_db.upload_file(image, image_path, compress=True)
            inventory.image_path = image_path

        self.firestore_db.create_document('inventory', inventory.__dict__)

    def get_inventory(self, inventory_id):
        inventory = self.firestore_db.get_document('inventory', inventory_id)
        return inventory

    def update_inventory(self, inventory_id, updates):
        self.firestore_db.update_document('inventory', inventory_id, updates)

    def delete_inventory(self, inventory_id):
        inventory = self.get_inventory(inventory_id)
        if inventory['image_path']:
            self.blob_db.delete_file(inventory['image_path'])
        self.firestore_db.delete_document('inventory', inventory_id)

    def get_all_inventory(self):
        return self.firestore_db.get_collection('inventory')

    def create_inventory_from_order(self, order_id):
        """Creates an inventory item from an order"""
        order = self.get_order(order_id)
        if not order:
            raise ValueError("Order not found")

        # Create inventory with same details as order
        inventory = {
            'id': str(uuid.uuid4()),
            'name': order['name'],
            'description': order.get('description', ''),
            'quantity': order['quantity'],
            'price': order.get('price', 0),
            'notes': order.get('notes', ''),
            'image_path': None,
            'created_from_order': order_id,
            'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Copy image if exists
        if order.get('image_path'):
            new_image_path = f"images/inventory/{inventory['id']}.jpg"
            self.blob_db.copy_file(order['image_path'], new_image_path)
            inventory['image_path'] = new_image_path

        self.firestore_db.create_document('inventory', inventory)
        return inventory['id']