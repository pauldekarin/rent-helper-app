from View.UserScreen.user_screen import UserScreenView
from Model.user_screen import UserScreenModel


class UserScreenContoller:
    def __init__(self, model:UserScreenModel, m_controller = None, name = None):
        self.model = model
        self.view = UserScreenView(controller = self, model = model)
        self.name = name

        self.m_controller = m_controller

    def onSubmit(self, username:str, password:str, type:str):
        if type == 'SIGN_IN':
            self.m_controller.onSignIn(username, password)
        else:
            self.m_controller.onSignUp(username, password)

    def onLogout(self):
        self.m_controller.onLogout()
        
    def setUser(self, user:dict):
        self.model.setUser(user)

    def onStart(self):
        self.model.onStart()
        
    def logout(self):
        self.model.logout()
        
    def sign_in(self, email, password):
        self.model.sign_in(email, password)
        
    def sign_up(self, email, password):
        self.model.sign_up(email, password)
    
    def on_start(self):
        self.model.on_start()
        
    def get_view(self)->UserScreenView:
        return self.view