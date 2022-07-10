import React, { Component } from "react";
import logo from "./logo.svg";
import "./App.css";

import {
    AdaptivityProvider,
    ConfigProvider,
    useAdaptivity,
    AppRoot,
    SplitLayout,
    HorizontalCell,
    Text,
    SplitCol,
    Tappable,
    ViewWidth,
    MiniInfoCell,
    Checkbox,
    View,
    Panel,
    Button,
    PanelHeader,
    Header,
    Group,
    SimpleCell,
} from "@vkontakte/vkui";
import DarkMode from "./DarkMode";
import "@vkontakte/vkui/dist/vkui.css";


class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            apiResponse: "Ваши письма",
            messages: [],
            checkboxes: {},
            theme: 'light'
        };

        this.gaps = {
            padding: 8,
            color: 'red'
        };

    }
    CheckboxChange(email, e) {

        this.state.checkboxes[email] = e.target.checked
    }


    callAPI() {
        fetch("http://localhost:9000/testAPI")
            .then(res => res.text())
            .then(res => this.setState({ messages: JSON.parse(res) }))
            .catch(err => err);
    }

    makeReadAPI() {
        let readMessages = []
        for (const [key, value] of Object.entries(this.state.checkboxes)) {
            if (value) {
                readMessages.push(key)
            }
        }


        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails: readMessages })
        };
        fetch("http://localhost:9000/testAPI/read", requestOptions)
            .then(res => res.text())
            .then(res => this.setState({ messages: JSON.parse(res) }))
            .catch(err => err);
    }

    makeUnreadAPI() {
        let readMessages = []
        for (const [key, value] of Object.entries(this.state.checkboxes)) {
            if (value) {
                readMessages.push(key)
            }
        }

        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails: readMessages })
        };
        fetch("http://localhost:9000/testAPI/unread", requestOptions)
            .then(res => res.text())
            .then(res => this.setState({ messages: JSON.parse(res) }))
            .catch(err => err);
    }

    switchTheme() {
        if (this.state.theme == 'dark')
            this.state.theme = 'light'
        else
            this.state.theme = 'dark'

        this.render()
    }

    componentDidMount() {
        this.callAPI();
    }

    render() {
        return (
            <AppRoot>
                <ConfigProvider appearance={this.state.theme}>
                    <SplitLayout header={<PanelHeader separator={false} />}>
                        <SplitCol>
                            <View activePanel="main">
                                <Panel id="main">
                                    <PanelHeader id='111'>{this.state.apiResponse}</PanelHeader>

                                    <Button onClick={() => this.switchTheme()}>
                                        {"Сменить тему"}
                                    </Button>
                                    <Button onClick={() => this.makeReadAPI()}>
                                        {"Пометить прочитанным"}
                                    </Button>
                                    <Button onClick={() => this.makeUnreadAPI()}>
                                        {"Пометить непрочитанным"}
                                    </Button>

                                    <Group header={<Header mode="secondary">Письма</Header>}>
                                        {this.state.messages.map((data, key) => {
                                            return <div style={this.gaps}><Tappable>
                                                <MiniInfoCell
                                                    before={<MiniInfoCell before={<Checkbox onChange={(e) => this.CheckboxChange(data.author.email, e)} description={data.read ? "прочитано" : "не прочитано"}></Checkbox>}>{data.author.name}</MiniInfoCell>}
                                                    after={<MiniInfoCell>{data.dateTime}</MiniInfoCell>}
                                                >
                                                    <MiniInfoCell before={<Text>{data.title}</Text>}>{data.text}</MiniInfoCell>
                                                </MiniInfoCell>
                                            </Tappable></div>
                                        })}
                                    </Group>
                                </Panel>
                            </View>
                        </SplitCol>
                    </SplitLayout>
                </ConfigProvider>
            </AppRoot >
        );
    }



}

export default App;
