from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import Legend,Panel,FactorRange,CheckboxButtonGroup,CheckboxGroup,LabelSet,RadioGroup, ColumnDataSource, Button, HoverTool,Div, Select, RadioButtonGroup
from bokeh.palettes import brewer, Set1,Turbo256
from bokeh.io.doc import curdoc
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select
from bokeh.transform import factor_cmap
import pandas as pd

from . import d_files
df = d_files.all_data["data"]

df_school = df[(df.age>=5)&(df.age<=15)].reset_index(drop = True)
print("Length of all currently attending df: ", len(df))
print("Length of only school attending df: ", len(df_school))

def data_filter(data,Gender,caste, clas):
    x = data[data["gender"].isin(Gender) & data["social_group"].isin(caste) & data["class"].isin(clas)]
    total = x.groupby(["inst_type","basic_course"]).agg({"weight":"sum"}).rename(
        columns =  {"weight":"t_weight"}).reset_index()
    ft = x.groupby(["inst_type",'pvt_coaching',"basic_course"]).agg({"weight":"sum"}).reset_index()
    merge = ft.merge(total, on = ["inst_type","basic_course"])
    if len(merge) == 0:
        merge = data.groupby(["inst_type","basic_course"]).size().to_frame("numbers").reset_index()
        merge["percentage"] = 0
    else:
        merge["percentage"] = round((merge.weight/merge.t_weight*100),2)
        merge = merge.query('pvt_coaching == "yes"')
        #merge = merge[merge["pvt_coaching"] == "yes"]
    merge = merge[["inst_type","basic_course","percentage"]]
    merge = merge.sort_values(["inst_type","basic_course"],ascending = [True,False])
    merge = merge.set_index(["inst_type","basic_course"])      
    return merge

def grouped_bar_color(df,y_val,title):
    """This plot will take 3 parameters, dataframe with multiindex index, name of the y-axis column and title.
    it will return a grouped bar graph"""
    df = df[[y_val]]
    x = df.index
    source = ColumnDataSource(data = dict(x = x,y_val = df[y_val]))
    color = df.reset_index()
    wid = list(color.iloc[:,0].unique())
    l = list(color.iloc[:,-2].unique())
    if len(wid) == 1:
        width = 600
    else:
        width = len(l)*len(wid)*85
        width = 800
    p = figure(x_range=FactorRange(*x),y_range = (0,60), plot_height=500, plot_width = width,title=title,
               toolbar_location="right",tools = "pan,wheel_zoom,box_zoom,reset,save")
    p.vbar(x= 'x', top="y_val", width=0.8, source=source, line_color="white",
           fill_color=factor_cmap('x', palette=Set1[len(l)], factors=l, start=1, end=2),
           hover_line_color = "darkgrey")
    p.add_tools(HoverTool(tooltips = [(y_val,"@y_val")]))
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None
    return p 


df_school["class"] = pd.qcut(df_school["hhd_exp"], 5, labels=["Very Low", "Low","Middle", "High", "Very High"])

x = data_filter(df_school,["female"],['others'] ,['Middle', 'Low', 'Very Low','High','Very High'])


p = grouped_bar_color(x,"percentage","Percentage of people opting for private coaching")


gen = list(df_school.gender.unique())
caste = list(df_school.social_group.unique())
clas = ['Very High','High', 'Middle','Low', 'Very Low']

gender = Div(text = """<u>Choose the gender below<u>""")
gend = CheckboxGroup(labels=["Female","Male"], active=[0, 1])

sog = Div(text = """<u>Choose the social group below<u>""")
cst = CheckboxGroup(labels=caste, active=[0,1,2,3])

inc = Div(text = """<u>Choose the class group below<u>""")
cls = CheckboxGroup(labels=clas, active=[0,1,2,3,4])

def update_data(attrname, old, new):
    gr = []
    sg = []
    claas = []
    for i in gend.active:
        gr.append(gen[i])
    for i in cst.active:
        sg.append(caste[i])
    for i in cls.active:
        claas.append(clas[i])
    x = data_filter(df_school,gr,sg,claas)
    p = grouped_bar_color(x,"percentage","percentage of people opting for private coaching")
    inputs.children[0] = p
gend.on_change("active",update_data)
cst.on_change("active",update_data)
cls.on_change("active",update_data)

inputs = column(p)
widgets = column(gender,gend,sog,cst,inc,cls)
layout = column(row(widgets,inputs))
curdoc().add_root(layout)
