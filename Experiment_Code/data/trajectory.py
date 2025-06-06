import matplotlib.pyplot as plt
import pandas as pd

participant_trialpath = 'data\participantid\participantid_trial1.csv'
df = pd.read_csv(participant_trialpath)

print(df['current_pos_x'])

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900

plt.xlim(-SCREEN_WIDTH/2, SCREEN_WIDTH/2)
plt.ylim(-SCREEN_HEIGHT/2, SCREEN_HEIGHT/2)

x = df['current_pos_x']
y = df['current_pos_y']

plt.plot(x, y)
plt.scatter(x, y)
plt.show()